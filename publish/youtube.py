"""Minimal YouTube Data API client for the Survra pipeline.

Secrets come ONLY from environment variables (GitHub encrypted secrets in CI,
or a local untracked secrets/ folder via load_local_env()). Nothing secret is
ever written to the repo or printed to logs.

Env:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
import json
import os
import random
import time

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"
RETRY_STATUS = {500, 502, 503, 504}
CHUNK = 8 * 1024 * 1024


class AuthExpired(RuntimeError):
    """Refresh token revoked or expired (Testing-mode tokens last 7 days)."""


def load_local_env(secrets_dir="secrets"):
    """Dev helper: fill env from the untracked secrets/ folder."""
    c = json.load(open(os.path.join(secrets_dir, "client_secret.json")))["installed"]
    t = json.load(open(os.path.join(secrets_dir, "token.json")))
    os.environ.setdefault("YT_CLIENT_ID", c["client_id"])
    os.environ.setdefault("YT_CLIENT_SECRET", c["client_secret"])
    os.environ.setdefault("YT_REFRESH_TOKEN", t["refresh_token"])


def _backoff(attempt):
    time.sleep(min(60, (2 ** attempt) + random.random()))


class YouTube:
    def __init__(self, session=None):
        self.s = session or requests.Session()
        self._tok = None
        self._exp = 0

    # ---- auth -------------------------------------------------------------
    def token(self):
        if self._tok and time.time() < self._exp - 60:
            return self._tok
        cid, sec, rt = (os.environ.get(k, "").strip().strip('"').strip("'")
                        for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
        r = self.s.post(TOKEN_URL, data=dict(client_id=cid, client_secret=sec, refresh_token=rt,
                                             grant_type="refresh_token"), timeout=30)
        if r.status_code >= 400:
            err = (r.json() if r.content else {}).get("error")
            if err == "invalid_grant":
                raise AuthExpired("Refresh token expired or revoked - re-authorize the Survra account.")
            # Safe diagnostics: shapes only, never values.
            raise RuntimeError(
                f"token endpoint {r.status_code} {err}: client_id looks "
                f"{'ok' if cid.endswith('.apps.googleusercontent.com') and cid[:1].isdigit() else 'WRONG'} (len {len(cid)}), "
                f"client_secret looks {'ok' if sec.startswith('GOCSPX-') and len(sec) == 35 else 'WRONG'} (len {len(sec)}), "
                f"refresh_token looks {'ok' if rt.startswith('1//') else 'WRONG'} (len {len(rt)})")
        j = r.json()
        self._tok, self._exp = j["access_token"], time.time() + j.get("expires_in", 3600)
        return self._tok

    def _h(self, extra=None):
        h = {"Authorization": "Bearer " + self.token()}
        h.update(extra or {})
        return h

    def _req(self, method, url, tries=5, **kw):
        for a in range(tries):
            r = self.s.request(method, url, headers=self._h(kw.pop("headers", None)), timeout=120, **kw)
            if r.status_code in RETRY_STATUS:
                _backoff(a)
                continue
            if r.status_code >= 400:
                raise RuntimeError(f"{method} {url.split('?')[0]} -> {r.status_code}: {r.text[:400]}")
            return r.json() if r.content else {}
        raise RuntimeError(f"{method} {url} failed after {tries} tries")

    # ---- reads ------------------------------------------------------------
    def my_channel(self):
        j = self._req("GET", f"{API}/channels", params=dict(part="snippet,statistics,status", mine="true"))
        return j["items"][0]

    def video_status(self, vid):
        j = self._req("GET", f"{API}/videos", params=dict(part="status,processingDetails,snippet", id=vid))
        return j["items"][0] if j.get("items") else None

    def recent_uploads(self, n=50):
        j = self._req("GET", f"{API}/search", params=dict(part="snippet", forMine="true", type="video", maxResults=min(n, 50)))
        return [dict(id=i["id"]["videoId"], title=i["snippet"]["title"]) for i in j.get("items", [])]

    # ---- writes -----------------------------------------------------------
    def upload(self, path, meta, log=print):
        """Resumable upload. meta keys: title, description, tags, category,
        privacy ('private'|'unlisted'|'public'), publish_at (RFC3339 or None),
        synthetic (bool: realistic altered/synthetic media disclosure)."""
        status = dict(privacyStatus=meta.get("privacy", "private"),
                      selfDeclaredMadeForKids=False,
                      embeddable=True, license="youtube")
        if meta.get("publish_at"):
            status["privacyStatus"] = "private"          # required for scheduling
            status["publishAt"] = meta["publish_at"]
        if meta.get("synthetic") is not None:
            status["containsSyntheticMedia"] = bool(meta["synthetic"])
        body = dict(
            snippet=dict(title=meta["title"][:100], description=meta.get("description", "")[:5000],
                         tags=meta.get("tags", [])[:30], categoryId=str(meta.get("category", 1)),
                         defaultLanguage="en", defaultAudioLanguage="en"),
            status=status)
        size = os.path.getsize(path)
        init = self.s.post(UPLOAD, params=dict(uploadType="resumable", part="snippet,status"),
                           headers=self._h({"Content-Type": "application/json; charset=UTF-8",
                                            "X-Upload-Content-Length": str(size),
                                            "X-Upload-Content-Type": "video/mp4"}),
                           data=json.dumps(body), timeout=60)
        if init.status_code >= 400:
            raise RuntimeError(f"upload init -> {init.status_code}: {init.text[:400]}")
        loc = init.headers["Location"]
        sent, attempt = 0, 0
        with open(path, "rb") as f:
            while sent < size:
                f.seek(sent)
                chunk = f.read(CHUNK)
                end = sent + len(chunk) - 1
                try:
                    r = self.s.put(loc, data=chunk, timeout=300, headers=self._h({
                        "Content-Length": str(len(chunk)),
                        "Content-Range": f"bytes {sent}-{end}/{size}"}))
                except requests.RequestException as e:
                    log(f"  chunk error {e.__class__.__name__}; resuming")
                    r = None
                if r is not None and r.status_code in (200, 201):
                    return r.json()
                if r is not None and r.status_code == 308:
                    rng = r.headers.get("Range")
                    sent = int(rng.split("-")[1]) + 1 if rng else 0
                    attempt = 0
                    log(f"  uploaded {sent / size:.0%}")
                    continue
                if r is not None and r.status_code not in RETRY_STATUS:
                    raise RuntimeError(f"upload chunk -> {r.status_code}: {r.text[:400]}")
                attempt += 1
                if attempt > 8:
                    raise RuntimeError("upload failed after retries")
                _backoff(attempt)
                q = self.s.put(loc, headers=self._h({"Content-Range": f"bytes */{size}", "Content-Length": "0"}), timeout=60)
                if q.status_code in (200, 201):
                    return q.json()
                rng = q.headers.get("Range")
                sent = int(rng.split("-")[1]) + 1 if rng else 0
        raise RuntimeError("upload ended without a response")

    def set_thumbnail(self, vid, png_path):
        ctype = "image/jpeg" if png_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        with open(png_path, "rb") as f:
            r = self.s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                            params=dict(videoId=vid), headers=self._h({"Content-Type": ctype}),
                            data=f.read(), timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"thumbnail -> {r.status_code}: {r.text[:300]}")
        return r.json()

    # ---- packaging ----------------------------------------------------------
    def upload_captions(self, vid, srt_path, lang="en", name="English"):
        """Uploads an SRT track. Needs the youtube.force-ssl scope; callers treat failure as non-fatal
        because captions are also burned into the picture."""
        boundary = "survra-captions-boundary"
        meta = json.dumps(dict(snippet=dict(videoId=vid, language=lang, name=name, isDraft=False)))
        body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n"
                f"--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + open(srt_path, "rb").read() + f"\r\n--{boundary}--".encode()
        r = self.s.post("https://www.googleapis.com/upload/youtube/v3/captions", params=dict(part="snippet", uploadType="multipart"),
                        headers=self._h({"Content-Type": f"multipart/related; boundary={boundary}"}), data=body, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"captions -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def ensure_playlist(self, title, description=""):
        page = None
        while True:
            params = dict(part="snippet", mine="true", maxResults=50)
            if page:
                params["pageToken"] = page
            j = self._req("GET", f"{API}/playlists", params=params)
            for it in j.get("items", []):
                if it["snippet"]["title"] == title:
                    return it["id"]
            page = j.get("nextPageToken")
            if not page:
                break
        j = self._req("POST", f"{API}/playlists", params=dict(part="snippet,status"),
                      json=dict(snippet=dict(title=title, description=description), status=dict(privacyStatus="public")))
        return j["id"]

    def add_to_playlist(self, playlist_id, vid):
        return self._req("POST", f"{API}/playlistItems", params=dict(part="snippet"),
                         json=dict(snippet=dict(playlistId=playlist_id, resourceId=dict(kind="youtube#video", videoId=vid))))
