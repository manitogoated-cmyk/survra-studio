"""Read-only channel audit for the Survra channel (runs on GitHub Actions, where the secrets live).

  python3 publish/audit.py OUT.json

Pulls everything the YouTube Data + Analytics APIs expose for this channel and writes one JSON file.
It never changes the channel: only GET requests. Every query is wrapped so one unsupported
metric/dimension combination is recorded under "errors" instead of stopping the audit.
Logs print counts only (the repo is public, so workflow logs are public).
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "publish"))
from youtube import YouTube, API  # noqa: E402

YTA = "https://youtubeanalytics.googleapis.com/v2/reports"
CFG = json.load(open(os.path.join(ROOT, "publish", "config.json")))
CORE = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost"

errors = []


def q(yt, label, **params):
    params.setdefault("ids", "channel==MINE")
    try:
        j = yt._req("GET", YTA, tries=2, params=params)
        cols = [c["name"] for c in j.get("columnHeaders", [])]
        return [dict(zip(cols, r)) for r in j.get("rows", [])]
    except Exception as ex:  # noqa: BLE001
        errors.append(dict(query=label, params={k: v for k, v in params.items() if k != "ids"}, error=str(ex)[:300]))
        return None


def main(out_path):
    yt = YouTube()
    ch = yt._req("GET", f"{API}/channels", params=dict(part="snippet,statistics,contentDetails", mine="true"))["items"][0]
    if ch["id"] != CFG["channel_id"]:
        raise SystemExit("REFUSING: token is not for the Survra channel")
    today = dt.date.today()
    created = ch["snippet"]["publishedAt"][:10]
    d90 = max(created, (today - dt.timedelta(days=90)).isoformat())
    end = today.isoformat()

    # every upload on the channel, not only the ones in the ledger
    vids, page = [], None
    while True:
        p = dict(part="contentDetails", playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"], maxResults=50)
        if page:
            p["pageToken"] = page
        j = yt._req("GET", f"{API}/playlistItems", params=p)
        vids += [it["contentDetails"]["videoId"] for it in j.get("items", [])]
        page = j.get("nextPageToken")
        if not page:
            break
    videos = {}
    for i in range(0, len(vids), 50):
        j = yt._req("GET", f"{API}/videos", params=dict(part="snippet,contentDetails,status,statistics", id=",".join(vids[i:i + 50])))
        for it in j.get("items", []):
            sn, st = it["snippet"], it["status"]
            videos[it["id"]] = dict(
                title=sn["title"], description=sn.get("description", ""), tags=sn.get("tags", []),
                published_at=sn.get("publishedAt"), publish_at=st.get("publishAt"), privacy=st["privacyStatus"],
                duration=it["contentDetails"]["duration"], made_for_kids=st.get("madeForKids"),
                stats={k: int(v) for k, v in it.get("statistics", {}).items()})

    res = dict(generated_utc=dt.datetime.utcnow().isoformat(timespec="seconds"), channel_id=ch["id"],
               channel_title=ch["snippet"]["title"], channel_created=created,
               channel_stats={k: int(v) if str(v).isdigit() else v for k, v in ch["statistics"].items()},
               ranges=dict(lifetime=[created, end], last90=[d90, end]), videos=videos)

    # channel level
    res["channel_daily"] = q(yt, "channel_daily", startDate=created, endDate=end, dimensions="day", metrics=CORE, sort="day")
    res["by_content_type"] = q(yt, "by_content_type", startDate=created, endDate=end, dimensions="creatorContentType", metrics=CORE)
    res["traffic_sources"] = q(yt, "traffic_sources", startDate=created, endDate=end, dimensions="insightTrafficSourceType", metrics="views,estimatedMinutesWatched")
    res["devices"] = q(yt, "devices", startDate=created, endDate=end, dimensions="deviceType", metrics="views,estimatedMinutesWatched")
    res["countries"] = q(yt, "countries", startDate=created, endDate=end, dimensions="country", metrics="views,estimatedMinutesWatched,averageViewPercentage", sort="-views", maxResults=25)
    res["subscribed_status"] = q(yt, "subscribed_status", startDate=created, endDate=end, dimensions="subscribedStatus", metrics="views,averageViewDuration,averageViewPercentage")
    res["demographics"] = q(yt, "demographics", startDate=created, endDate=end, dimensions="ageGroup,gender", metrics="viewerPercentage")

    # per video, two windows
    for label, start in (("per_video_lifetime", created), ("per_video_90d", d90)):
        res[label] = q(yt, label, startDate=start, endDate=end, dimensions="video", metrics=CORE, sort="-views", maxResults=200)
    res["per_video_engaged"] = q(yt, "per_video_engaged", startDate=created, endDate=end, dimensions="video", metrics="views,engagedViews", sort="-views", maxResults=200)
    res["per_video_impressions"] = q(yt, "per_video_impressions", startDate=created, endDate=end, dimensions="video",
                                     metrics="videoThumbnailImpressions,videoThumbnailImpressionsClickRate", sort="-videoThumbnailImpressions", maxResults=200)

    # deep per-video reports for anything that has been public
    live = [v for v, m in videos.items() if m["privacy"] == "public"]
    res["video_daily"], res["video_traffic"], res["video_retention"], res["comments"] = {}, {}, {}, {}
    for v in live:
        f = f"video=={v}"
        res["video_daily"][v] = q(yt, f"daily:{v}", startDate=created, endDate=end, dimensions="day", filters=f, metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained,likes,shares", sort="day")
        res["video_traffic"][v] = q(yt, f"traffic:{v}", startDate=created, endDate=end, dimensions="insightTrafficSourceType", filters=f, metrics="views,estimatedMinutesWatched")
        res["video_retention"][v] = q(yt, f"retention:{v}", startDate=created, endDate=end, dimensions="elapsedVideoTimeRatio", filters=f,
                                      metrics="audienceWatchRatio,relativeRetentionPerformance")
        try:  # comment text only, no author names
            j = yt._req("GET", f"{API}/commentThreads", tries=2, params=dict(part="snippet", videoId=v, maxResults=100, order="relevance", textFormat="plainText"))
            res["comments"][v] = [dict(text=t["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                       likes=t["snippet"]["topLevelComment"]["snippet"].get("likeCount", 0),
                                       replies=t["snippet"].get("totalReplyCount", 0),
                                       at=t["snippet"]["topLevelComment"]["snippet"]["publishedAt"]) for t in j.get("items", [])]
        except Exception as ex:  # noqa: BLE001
            errors.append(dict(query=f"comments:{v}", error=str(ex)[:300]))

    res["errors"] = errors
    json.dump(res, open(out_path, "w"), indent=1)
    print(f"audit: {len(videos)} uploads, {len(live)} public, {len(errors)} query errors")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "audit.json"))
