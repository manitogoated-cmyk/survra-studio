"""Survra publisher: render -> QC gate -> upload -> ledger.

Episode folders live in episodes/<id>/ and contain:
  episode.json   metadata + workflow status
  script.json    narration (engine/voice.py format)
  storyboard.json shot list (engine2/render.py format)

episode.json fields
  id, format ("short"|"long"), title, description, tags[], sources[]
  status: "draft"     - being written, never rendered
          "ready"     - script+storyboard done; CI renders and QCs it
          "approved"  - human/automated review passed; may be scheduled public
  synthetic: bool     - realistic altered/synthetic media? (stylised cartoons = false)

Safety rails
  * publish/config.json "paused": true  -> nothing is uploaded.
  * "review_mode": true -> every upload is PRIVATE with no publish date, so the
    owner can review the batch in YouTube Studio before anything goes public.
  * Ledger (publish/ledger.json) keyed by episode id AND file sha256 blocks
    duplicate uploads, even across reruns.
  * QC FAIL -> never uploaded.
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from publish.youtube import YouTube, AuthExpired  # noqa: E402

CFG = os.path.join(ROOT, "publish", "config.json")
LEDGER = os.path.join(ROOT, "publish", "ledger.json")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def log(*a):
    print(dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S"), *a, flush=True)


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def save(p, obj):
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=2, sort_keys=True)
    os.replace(tmp, p)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def episodes():
    for p in sorted(glob.glob(os.path.join(ROOT, "episodes", "*", "episode.json"))):
        e = json.load(open(p))
        e["_dir"] = os.path.dirname(p)
        yield e


def render(e):
    out = os.path.join(e["_dir"], e["id"] + ".mp4")
    if e.get("format", "short") != "short":
        raise NotImplementedError("long-form renderer not wired yet")
    r = subprocess.run(["bash", os.path.join(ROOT, "engine2", "make_short.sh"), e["_dir"], e["id"]],
                       capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    qc = load(os.path.join(e["_dir"], "build", "qc.json"), {})
    return out, r.returncode == 0 and qc.get("pass") is True, qc


def next_slot(cfg, ledger, fmt, now=None):
    """Earliest free local slot from tomorrow onward, returned as RFC3339 UTC."""
    tz = ZoneInfo(cfg["timezone"])
    now = now or dt.datetime.now(tz)
    taken = {v.get("publish_at") for v in ledger.values()}
    for d in range(1, 60):
        day = (now + dt.timedelta(days=d)).date()
        if fmt == "short":
            times = cfg["short_slots_local"]
        else:
            t = cfg["long_slots_local"].get(DAYS[day.weekday()])
            times = [t] if t else []
        for t in times:
            hh, mm = map(int, t.split(":"))
            local = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
            iso = local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if iso not in taken:
                return iso
    raise RuntimeError("no free slot in the next 60 days")


def description(e):
    d = e.get("description", "").strip()
    src = e.get("sources") or []
    if src:
        d += "\n\nSources:\n" + "\n".join("- " + s for s in src)
    d += "\n\nAnimated by Survra. Narration is AI-generated; story researched from the sources above."
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="episode id to process")
    ap.add_argument("--dry-run", action="store_true", help="render + QC, never upload")
    ap.add_argument("--skip-render", action="store_true", help="use an existing mp4")
    args = ap.parse_args()

    cfg, ledger = load(CFG, {}), load(LEDGER, {})
    if cfg.get("paused"):
        log("PAUSED via publish/config.json - nothing to do")
        return 0
    yt = None if args.dry_run else YouTube()
    if yt:
        ch = yt.my_channel()
        if ch["id"] != cfg["channel_id"]:
            log("REFUSING: token belongs to", ch["snippet"]["title"], "not the Survra channel")
            return 3
        log("channel OK:", ch["snippet"]["title"])

    done, failures = 0, []
    hashes = {v.get("sha256") for v in ledger.values()}
    for e in episodes():
        if args.only and e["id"] != args.only:
            continue
        if e["id"] in ledger or e.get("status") not in ("ready", "approved"):
            continue
        if done >= cfg.get("max_uploads_per_run", 4):
            break
        log("episode", e["id"])
        mp4 = os.path.join(e["_dir"], e["id"] + ".mp4")
        if args.skip_render and os.path.exists(mp4):
            qc = load(os.path.join(e["_dir"], "build", "qc.json"), {"pass": None}); ok = qc.get("pass") is True
        else:
            mp4, ok, qc = render(e)
        if not ok:
            log("  QC FAIL - not uploading:", json.dumps(qc.get("fails", qc))[:500])
            failures.append(e["id"])
            continue
        h = sha256(mp4)
        if h in hashes:
            log("  duplicate file already uploaded - skipping")
            continue
        if args.dry_run:
            log("  dry run: QC PASS, would upload", mp4)
            continue
        review = cfg.get("review_mode", True) or e.get("status") != "approved"
        meta = dict(title=e["title"], description=description(e), tags=e.get("tags", []),
                    category=cfg.get("category_id", 1), synthetic=e.get("synthetic", False))
        if review:
            meta["privacy"] = "private"
        else:
            meta["publish_at"] = next_slot(cfg, ledger, e.get("format", "short"))
        try:
            res = yt.upload(mp4, meta, log=log)
        except AuthExpired as ex:
            log("AUTH EXPIRED:", ex)
            return 2
        except Exception as ex:  # keep going with other episodes
            log("  upload failed:", ex)
            failures.append(e["id"])
            continue
        vid = res["id"]
        ledger[e["id"]] = dict(video_id=vid, sha256=h, uploaded_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                               publish_at=meta.get("publish_at"), privacy=res["status"]["privacyStatus"],
                               review=review, title=e["title"])
        save(LEDGER, ledger)
        hashes.add(h)
        done += 1
        log(f"  uploaded https://youtu.be/{vid} privacy={res['status']['privacyStatus']} publishAt={meta.get('publish_at')}")
        thumb = os.path.join(e["_dir"], "thumbnail.png")
        if os.path.exists(thumb):
            try:
                yt.set_thumbnail(vid, thumb)
            except Exception as ex:
                log("  thumbnail failed (channel may need phone verification):", ex)
    log(f"done: {done} uploaded, {len(failures)} failed {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
