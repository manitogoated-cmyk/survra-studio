"""Channel operations that need the YouTube API (run on GitHub Actions, where the secrets live).

  python3 publish/ops.py brand       upload brand/rook_banner_2560x1440.jpg + brand/rook_watermark_150.png to the Survra channel
  python3 publish/ops.py release     make approved episodes that were uploaded privately for review public
  python3 publish/ops.py analytics   write ANALYTICS.md + plan/learnings.json from real channel numbers (weekly)
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "publish"))
from youtube import YouTube, AuthExpired  # noqa: E402

CFG = json.load(open(os.path.join(ROOT, "publish", "config.json")))


def channel(yt):
    ch = yt.my_channel()
    if ch["id"] != CFG["channel_id"]:
        raise SystemExit("REFUSING: token belongs to " + ch["snippet"]["title"] + ", not the Survra channel")
    return ch


ABOUT = """Rook's Case Files: unbelievable true stories, checked by one sceptical crow.

Rook is a detective who does not believe a word of it. Every video is a case: a survival story, a rescue, a mystery that sounds impossible. He goes to look, and reports what actually happened.

Original 3D animation. Every case is researched from named sources, listed in each description. Narration is a synthetic voice.

New Shorts and full case files every week.

About, privacy and contact: https://manitogoated-cmyk.github.io/survra/"""
KEYWORDS = '"true stories" "survival stories" "animated stories" "3D animation" Rook Survra "case files" documentary mystery rescue'


def brand():
    yt = YouTube()
    ch = channel(yt)
    res = {}
    for name, fn in (("banner", lambda: yt.set_banner(os.path.join(ROOT, "brand", "rook_banner_2560x1440.jpg"))),
                     ("watermark", lambda: yt.set_watermark(os.path.join(ROOT, "brand", "rook_watermark_150.png"), ch["id"])),
                     ("about", lambda: yt.set_channel_text(ABOUT, KEYWORDS))):
        try:
            fn(); res[name] = "ok"
        except AuthExpired:
            raise
        except Exception as ex:
            res[name] = "failed: " + str(ex)[:300]
    print(json.dumps(res, indent=1))
    return 0 if all(v == "ok" for v in res.values()) else 1


def analytics():
    yt = YouTube()
    ch = channel(yt)
    ledger = json.load(open(os.path.join(ROOT, "publish", "ledger.json")))
    ids = {v["video_id"]: k for k, v in ledger.items() if v.get("video_id")}
    stats = yt.video_stats(list(ids)) if ids else {}
    today = dt.date.today()
    deep, note = {}, ""
    try:
        deep = yt.analytics((today - dt.timedelta(days=28)).isoformat(), today.isoformat())
    except Exception as ex:
        note = f"Retention data unavailable ({str(ex)[:160]}). Enable the YouTube Analytics API in the Google Cloud project to get it."
    rows, learn = [], []
    for vid, ep in ids.items():
        s, d = stats.get(vid, {}), deep.get(vid, {})
        rows.append((ep, ledger[ep].get("format", "short"), s.get("privacy", "?"), s.get("viewCount", 0), s.get("likeCount", 0), s.get("commentCount", 0),
                     d.get("averageViewPercentage", "-"), d.get("averageViewDuration", "-"), d.get("subscribersGained", "-"), d.get("shares", "-")))
        if s.get("privacy") == "public" and isinstance(d.get("averageViewPercentage"), (int, float)):
            avp = d["averageViewPercentage"]
            fmt = ledger[ep].get("format", "short")
            if fmt == "short" and avp < 70:
                learn.append(dict(episode=ep, signal=f"Short watched {avp:.0f}% on average (target 70%+)", action="Tighten the first three seconds and cut the slowest middle beat in the next scripts."))
            if fmt == "long" and avp < 40:
                learn.append(dict(episode=ep, signal=f"Long-form watched {avp:.0f}% on average (target 40%+)", action="Add a stronger mid-video reversal and shorten the setup."))
            if s.get("viewCount", 0) >= 200 and d.get("subscribersGained", 0) == 0:
                learn.append(dict(episode=ep, signal="Views without subscribers", action="Make Rook's sign-off promise the next case more concretely."))
    public = [r for r in rows if r[2] == "public"]
    best = max(public, key=lambda r: r[3], default=None)
    st = ch["statistics"]
    out = ["# Survra analytics", "", f"Updated {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC by the weekly analytics workflow. Numbers come from the YouTube API; nothing here is estimated.", "",
           f"Channel: **{st.get('subscriberCount', '0')}** subscribers, **{st.get('viewCount', '0')}** views, **{st.get('videoCount', '0')}** videos ({len(public)} public from this pipeline).", ""]
    if note:
        out += [note, ""]
    out += ["| Episode | Format | Privacy | Views | Likes | Comments | Avg % watched | Avg view (s) | Subs gained | Shares |", "|---|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in sorted(rows, key=lambda r: -r[3])]
    out += ["", "## What the numbers say"]
    if not public:
        out += ["No public videos yet, so there is nothing to learn from. The first public cases will fill this in."]
    else:
        out += [f"- Best performer: `{best[0]}` with {best[3]} views. Next cases should reuse what made its hook work, with a new story and world."]
        out += [f"- `{l['episode']}`: {l['signal']}. {l['action']}" for l in learn] or ["- No weak signals this week."]
    open(os.path.join(ROOT, "ANALYTICS.md"), "w").write("\n".join(out) + "\n")
    json.dump(dict(updated=today.isoformat(), best=best[0] if best else None, learnings=learn), open(os.path.join(ROOT, "plan", "learnings.json"), "w"), indent=1)
    print("\n".join(out[:12]))
    return 0


def release():
    """Makes approved episodes that were uploaded privately for review public now. Never touches anything else."""
    yt = YouTube()
    channel(yt)
    lp = os.path.join(ROOT, "publish", "ledger.json")
    ledger = json.load(open(lp))
    bad = 0
    for ep, row in ledger.items():
        ej = os.path.join(ROOT, "episodes", ep, "episode.json")
        if not os.path.exists(ej) or json.load(open(ej)).get("status") != "approved":
            continue
        if row.get("privacy") == "public" or not row.get("video_id"):
            continue
        try:
            st = yt.set_privacy(row["video_id"], "public")
        except AuthExpired:
            raise
        except Exception as ex:
            print(ep, "release failed:", str(ex)[:400]); row["release_error"] = str(ex)[:300]; bad += 1
            continue
        row.update(privacy=st.get("privacyStatus"), review=False, upload_status=st.get("uploadStatus"),
                   released_at=dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        row.pop("release_error", None)
        print(ep, row["url"], "->", st.get("privacyStatus"), "| uploadStatus", st.get("uploadStatus"),
              "| rejection", st.get("rejectionReason"), "| failure", st.get("failureReason"))
        if st.get("privacyStatus") != "public":
            bad += 1
    json.dump(ledger, open(lp, "w"), indent=2, sort_keys=True)
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(dict(brand=brand, analytics=analytics, release=release)[sys.argv[1]]())
    except AuthExpired as ex:
        print("AUTH EXPIRED:", ex); sys.exit(2)
