"""Append one audit snapshot to the permanent performance database.

  python3 publish/audit_db.py audit.json

Writes (append-only, history is never rewritten):
  analytics/video-performance.csv   one row per video per snapshot: live counters, Analytics API
                                    metrics, retention checkpoints, traffic mix and creative tags
  analytics/channel-history.csv     one row per snapshot: channel totals and format split
Run it after every publish cycle (or weekly) on a fresh publish/audit.py output.
Blank cell = the API did not return that value yet (normal for ~2-3 days after publishing). Never fill blanks by hand.
"""
import csv
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analytics")

VCOLS = ["snapshot_utc", "episode", "video_id", "format", "privacy", "title", "duration_s", "public_at_utc", "age_h",
         "views", "likes", "comments",
         "api_data_through", "api_views", "engaged_views", "engaged_ratio", "minutes_watched", "avg_view_s", "avg_view_pct",
         "shares", "subs_gained", "subs_lost", "likes_per_1k", "subs_per_1k",
         "ret_00", "ret_10", "ret_20", "ret_30", "ret_50", "ret_90", "rel_retention",
         "traffic_shorts_pct", "traffic_browse_pct", "traffic_suggested_pct", "traffic_search_pct",
         "spine", "hook_line", "first_shot", "first_shot_action", "first_rook_shot", "shots", "segments", "words", "ending"]
CCOLS = ["snapshot_utc", "api_data_through", "subscribers", "total_views", "public_videos",
         "shorts_views", "shorts_avg_view_pct", "long_views", "long_avg_view_pct", "subs_gained", "subs_lost"]


def secs(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else ""


def plain(t):
    return re.sub(r"\{[^|}]*\|([^}]*)\}", r"\1", t)


def tags(ep):
    """Creative tags read from the episode's own source files (what was actually made)."""
    d = os.path.join(ROOT, "episodes", ep or "_none_")
    t = dict(spine="", hook_line="", first_shot="", first_shot_action="", first_rook_shot="", shots="", segments="", words="", ending="")
    try:
        sc = json.load(open(os.path.join(d, "script.json"), encoding="utf-8"))
        segs = sc.get("segments", [])
        names = [s.get("scene") for s in segs]
        t.update(hook_line=plain(segs[0]["text"]) if segs else "", segments=len(segs),
                 words=sum(len(plain(s["text"]).split()) for s in segs),
                 ending="question" if segs and "?" in segs[-1]["text"] else "closed",
                 spine=sc.get("spine") or ("v1-doubt-cutaway" if len(names) > 1 and names[1] == "doubt" else "other"))
        sb = json.load(open(os.path.join(d, "storyboard.json"), encoding="utf-8")).get("shots", [])
        t.update(shots=len(sb), first_shot=sb[0]["kind"] if sb else "", first_shot_action=sb[0].get("action", "")[:120] if sb else "",
                 first_rook_shot=next((i + 1 for i, s in enumerate(sb) if "rook" in s.get("kind", "")), ""))
    except (OSError, ValueError, KeyError):
        pass
    return t


def at(curve, x):
    """audienceWatchRatio at the checkpoint nearest to x (0..1)."""
    if not curve:
        return ""
    return round(min(curve, key=lambda r: abs(r["elapsedVideoTimeRatio"] - x))["audienceWatchRatio"], 3)


def append(path, cols, rows):
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerows(rows)


def main(src):
    a = json.load(open(src, encoding="utf-8"))
    ledger = json.load(open(os.path.join(ROOT, "publish", "ledger.json"), encoding="utf-8"))
    ep_of = {v["video_id"]: k for k, v in ledger.items() if v.get("video_id")}
    snap = a["generated_utc"]
    now = dt.datetime.fromisoformat(snap)
    life = {r["video"]: r for r in (a.get("per_video_lifetime") or [])}
    eng = {r["video"]: r for r in (a.get("per_video_engaged") or [])}
    days = [r["day"] for r in (a.get("channel_daily") or []) if r.get("views")]
    through = max(days) if days else ""
    rows = []
    for vid, m in a["videos"].items():
        ep = ep_of.get(vid, "")
        s, L, E = m.get("stats", {}), life.get(vid, {}), eng.get(vid, {})
        pub = (m.get("publish_at") or m.get("published_at") or "").replace("Z", "")
        age = round((now - dt.datetime.fromisoformat(pub)).total_seconds() / 3600, 1) if pub and m["privacy"] == "public" else ""
        fmt = ledger.get(ep, {}).get("format") or ("short" if (secs(m["duration"]) or 999) <= 180 and "#shorts" in m["title"] else "long")
        tr = {r["insightTrafficSourceType"]: r["views"] for r in (a.get("video_traffic", {}).get(vid) or [])}
        tot = sum(tr.values()) or 0
        pct = (lambda k: round(100 * tr.get(k, 0) / tot, 1) if tot else "")
        cur = a.get("video_retention", {}).get(vid) or []
        av = L.get("views") or 0
        rows.append(dict(
            snapshot_utc=snap, episode=ep, video_id=vid, format=fmt, privacy=m["privacy"], title=m["title"], duration_s=secs(m["duration"]),
            public_at_utc=pub if m["privacy"] == "public" else "", age_h=age,
            views=s.get("viewCount", ""), likes=s.get("likeCount", ""), comments=s.get("commentCount", ""),
            api_data_through=through if L else "", api_views=L.get("views", ""), engaged_views=E.get("engagedViews", ""),
            engaged_ratio=round(E["engagedViews"] / E["views"], 3) if E.get("views") else "",
            minutes_watched=L.get("estimatedMinutesWatched", ""), avg_view_s=L.get("averageViewDuration", ""),
            avg_view_pct=round(L["averageViewPercentage"], 1) if L.get("averageViewPercentage") is not None else "",
            shares=L.get("shares", ""), subs_gained=L.get("subscribersGained", ""), subs_lost=L.get("subscribersLost", ""),
            likes_per_1k=round(1000 * L["likes"] / av, 1) if av else "", subs_per_1k=round(1000 * L["subscribersGained"] / av, 2) if av else "",
            ret_00=at(cur, 0.01), ret_10=at(cur, 0.1), ret_20=at(cur, 0.2), ret_30=at(cur, 0.3), ret_50=at(cur, 0.5), ret_90=at(cur, 0.9),
            rel_retention=round(sum(r["relativeRetentionPerformance"] for r in cur) / len(cur), 3) if cur else "",
            traffic_shorts_pct=pct("SHORTS"), traffic_browse_pct=pct("SUBSCRIBER"), traffic_suggested_pct=pct("RELATED_VIDEO"), traffic_search_pct=pct("YT_SEARCH"),
            **tags(ep)))
    os.makedirs(OUT, exist_ok=True)
    append(os.path.join(OUT, "video-performance.csv"), VCOLS, sorted(rows, key=lambda r: (r["format"], r["public_at_utc"] or "~")))
    ct = {r["creatorContentType"]: r for r in (a.get("by_content_type") or [])}
    sh, lo = ct.get("shorts", {}), ct.get("videoOnDemand", {})
    cs = a.get("channel_stats", {})
    daily = a.get("channel_daily") or []
    append(os.path.join(OUT, "channel-history.csv"), CCOLS, [dict(
        snapshot_utc=snap, api_data_through=through, subscribers=cs.get("subscriberCount", ""), total_views=cs.get("viewCount", ""),
        public_videos=sum(1 for m in a["videos"].values() if m["privacy"] == "public"),
        shorts_views=sh.get("views", ""), shorts_avg_view_pct=round(sh["averageViewPercentage"], 1) if sh.get("averageViewPercentage") else "",
        long_views=lo.get("views", ""), long_avg_view_pct=round(lo["averageViewPercentage"], 1) if lo.get("averageViewPercentage") else "",
        subs_gained=sum(r.get("subscribersGained", 0) for r in daily), subs_lost=sum(r.get("subscribersLost", 0) for r in daily))])
    print(f"appended {len(rows)} video rows and 1 channel row for snapshot {snap}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "audit.json")
