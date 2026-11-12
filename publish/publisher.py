"""Survra production queue: plan -> render (parallel) -> upload (serial) -> status dashboard.

  python3 publish/publisher.py plan                 # JSON list of episode ids that need rendering
  python3 publish/publisher.py render --only <id>   # voice + animation + sound + QC gate + packaging
  python3 publish/publisher.py upload               # upload everything rendered and QC-passed
  python3 publish/publisher.py status               # rewrite STATUS.md (the production dashboard)

Episode status in episode.json: draft -> ready (render it) -> approved (may be scheduled public).
Safety rails: config "paused"; "review_mode" (uploads stay PRIVATE, unscheduled); QC FAIL never uploads;
ledger by episode id + file hash blocks duplicates; token must belong to the Survra channel.
"""
import argparse, datetime as dt, glob, hashlib, json, os, subprocess, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from publish.youtube import YouTube, AuthExpired  # noqa: E402

CFG = os.path.join(ROOT, "publish", "config.json")
LEDGER = os.path.join(ROOT, "publish", "ledger.json")
STATUS = os.path.join(ROOT, "STATUS.md")


def now():
    return dt.datetime.now(dt.timezone.utc)

def log(*a):
    print(now().strftime("%H:%M:%S"), *a, flush=True)

def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default

def save(p, obj):
    tmp = p + ".tmp"; json.dump(obj, open(tmp, "w"), indent=2, sort_keys=True); os.replace(tmp, p)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def episodes():
    for p in sorted(glob.glob(os.path.join(ROOT, "episodes", "*", "episode.json"))):
        e = json.load(open(p)); e["_dir"] = os.path.dirname(p); yield e

def hosted(e):
    return os.path.exists(os.path.join(e["_dir"], "scenes.py"))

def mp4(e):
    return os.path.join(e["_dir"], e["id"] + ".mp4")

def qc(e):
    return load(os.path.join(e["_dir"], "build", "qc.json"), {})


def plan(cfg, ledger):
    todo = [e["id"] for e in episodes() if e.get("status") in ("ready", "approved") and e["id"] not in ledger]
    return todo[: cfg.get("max_uploads_per_run", 6)]


def render(e):
    script = os.path.join(ROOT, "engine3", "make_episode.sh") if hosted(e) else os.path.join(ROOT, "engine2", "make_short.sh")
    args = ["bash", script, e["_dir"]] + ([] if hosted(e) else [e["id"]])
    for attempt in (1, 2):                      # retry once: render failures are usually transient
        r = subprocess.run(args, capture_output=True, text=True)
        print(r.stdout[-2500:], r.stderr[-1500:])
        if qc(e).get("pass") is True and r.returncode == 0:
            break
        if qc(e).get("fails"):                  # a real quality failure: do not retry, report it
            break
        log(f"  render attempt {attempt} failed without a QC verdict; retrying")
    ok = r.returncode == 0 and qc(e).get("pass") is True
    if ok and hosted(e):
        from engine3 import package
        package.srt(e["_dir"]); package.thumbnail(e["_dir"])
    return ok


def next_slot(cfg, ledger, fmt, now_=None):
    tz = ZoneInfo(cfg["timezone"]); now_ = now_ or dt.datetime.now(tz)
    taken = {v.get("publish_at") for v in ledger.values()}
    for d in range(1, 90):
        day = (now_ + dt.timedelta(days=d)).date()
        for t in cfg["short_slots_local" if fmt == "short" else "long_slots_local"]:
            hh, mm = map(int, t.split(":"))
            iso = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if iso not in taken: return iso
    raise RuntimeError("no free slot in the next 90 days")


def description(e):
    if hosted(e):
        from engine3 import package
        return package.description(e)
    d = e.get("description", "").strip()
    if e.get("sources"): d += "\n\nSources:\n" + "\n".join("- " + s for s in e["sources"])
    return d + "\n\nAnimated by Survra. Narration is AI-generated; story researched from the sources above."


def upload(cfg, ledger, only=None):
    yt = YouTube(); ch = yt.my_channel()
    if ch["id"] != cfg["channel_id"]:
        log("REFUSING: token belongs to", ch["snippet"]["title"], "not the Survra channel"); return 3
    log("channel OK:", ch["snippet"]["title"])
    done, failures = 0, []
    hashes = {v.get("sha256") for v in ledger.values()}
    for e in episodes():
        if (only and e["id"] != only) or e["id"] in ledger or e.get("status") not in ("ready", "approved"): continue
        if done >= cfg.get("max_uploads_per_run", 6): break
        if not os.path.exists(mp4(e)) or qc(e).get("pass") is not True:
            log("skip", e["id"], "- not rendered or QC not passed:", json.dumps(qc(e).get("fails", "no render"))[:300])
            failures.append(e["id"]); continue
        h = sha256(mp4(e))
        if h in hashes: log("skip", e["id"], "- identical file already uploaded"); continue
        review = cfg.get("review_mode", True) or e.get("status") != "approved"
        fmt = e.get("format", "short")
        meta = dict(title=e["title"], description=description(e), tags=e.get("tags", []), category=cfg.get("category_id", 1),
                    synthetic=e.get("synthetic", False))
        if review: meta["privacy"] = "private"
        else: meta["publish_at"] = next_slot(cfg, ledger, fmt)
        try:
            res = yt.upload(mp4(e), meta, log=log)
        except AuthExpired as ex:
            log("AUTH EXPIRED:", ex); return 2
        except Exception as ex:
            log("  upload failed:", ex); failures.append(e["id"]); continue
        vid = res["id"]; extras = {}
        build = os.path.join(e["_dir"], "build")
        for name, path, fn in (("thumbnail", os.path.join(build, "thumbnail.jpg"), lambda p: yt.set_thumbnail(vid, p)),
                               ("captions", os.path.join(build, "captions.srt"), lambda p: yt.upload_captions(vid, p))):
            if name == "thumbnail" and fmt == "short": continue     # Shorts covers cannot be set through the API
            if os.path.exists(path):
                try: fn(path); extras[name] = "ok"
                except Exception as ex: extras[name] = "failed: " + str(ex)[:160]; log(f"  {name} failed:", ex)
        if e.get("playlist"):
            try: yt.add_to_playlist(yt.ensure_playlist(e["playlist"]), vid); extras["playlist"] = e["playlist"]
            except Exception as ex: extras["playlist"] = "failed: " + str(ex)[:160]; log("  playlist failed:", ex)
        ledger[e["id"]] = dict(video_id=vid, url=f"https://youtu.be/{vid}", sha256=h, uploaded_at=now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                               publish_at=meta.get("publish_at"), privacy=res["status"]["privacyStatus"], review=review,
                               title=e["title"], format=fmt, **extras)
        save(LEDGER, ledger); hashes.add(h); done += 1
        log(f"  uploaded https://youtu.be/{vid} privacy={res['status']['privacyStatus']} publishAt={meta.get('publish_at')} {extras}")
    log(f"done: {done} uploaded, {len(failures)} not uploaded {failures}")
    return 1 if failures else 0


def status(cfg, ledger):
    """Production dashboard. A stage is only ticked when its real output exists and was verified."""
    rows = []
    for e in episodes():
        d = e["_dir"]; has = lambda *p: os.path.exists(os.path.join(d, *p))
        q = qc(e); L = ledger.get(e["id"], {})
        tick = lambda ok, bad=False: "FAIL" if bad else ("done" if ok else "-")
        pub = "-"
        if L: pub = "private (review)" if L.get("review") else ("scheduled " + (L.get("publish_at") or "")) if L.get("publish_at") else L.get("privacy", "-")
        rows.append([e["id"], e.get("format", "short"), e.get("status", "draft"), tick(bool(e.get("sources"))), tick(has("script.json")),
                     tick(has("storyboard.json")), tick(has("scenes.py") or not hosted(e)), tick(has("build", "voice.wav") or bool(L)),
                     tick(os.path.exists(mp4(e)) or bool(L)), tick(has("build", "thumbnail.jpg") or L.get("thumbnail") == "ok") if e.get("format") == "long" else "n/a",
                     tick(q.get("pass") is True or bool(L), q.get("pass") is False), tick(bool(L)), pub, L.get("url") or ("https://youtu.be/" + L["video_id"] if L.get("video_id") else "-")])
    head = ["Episode", "Format", "Status", "Research", "Script", "Storyboard", "Animation", "Voice", "Edit", "Thumbnail", "QC", "Upload", "Publication", "URL"]
    t = cfg.get("daily_target", {})
    out = ["# Survra production dashboard", "", f"Updated {now().strftime('%Y-%m-%d %H:%M UTC')} by the publish workflow. "
           f"Daily target: {t.get('long', 0)} long-form + {t.get('short', 0)} Shorts. Review mode: **{'ON' if cfg.get('review_mode') else 'off'}**. "
           f"Paused: **{'yes' if cfg.get('paused') else 'no'}**.", "",
           "A stage shows `done` only when its output file exists; QC shows `done` only after the automated gate passed on the rendered video.", "",
           "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    open(STATUS, "w").write("\n".join(out) + "\n")
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "render", "upload", "status"]); ap.add_argument("--only")
    a = ap.parse_args(); cfg, ledger = load(CFG, {}), load(LEDGER, {})
    if a.cmd == "plan":
        print(json.dumps([] if cfg.get("paused") else ([a.only] if a.only else plan(cfg, ledger)))); return 0
    if a.cmd == "status": return status(cfg, ledger)
    if cfg.get("paused"): log("PAUSED via publish/config.json"); return 0
    if a.cmd == "render":
        e = next(x for x in episodes() if x["id"] == a.only); ok = render(e)
        log("render", e["id"], "QC PASS" if ok else "QC FAIL / render error"); return 0 if ok else 1
    return upload(cfg, ledger, a.only)


if __name__ == "__main__":
    sys.exit(main())
