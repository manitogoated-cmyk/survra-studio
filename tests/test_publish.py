import json, os, sys, tempfile, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from publish import youtube, publisher

class R:
    def __init__(s, code, js=None, headers=None):
        s.status_code, s._js, s.headers = code, js or {}, headers or {}
        s.content = b'x' if js is not None else b''
        s.text = json.dumps(s._js)
    def json(s): return s._js
    def raise_for_status(s):
        if s.status_code >= 400: raise RuntimeError(s.status_code)

class FakeSession:
    """Token ok; resumable upload: one 503, then 308 partial, then 200."""
    def __init__(s): s.calls = []; s.put_n = 0
    def post(s, url, **kw):
        s.calls.append(('POST', url))
        if 'token' in url: return R(200, {'access_token': 'a', 'expires_in': 3600})
        return R(200, {}, {'Location': 'https://upload/loc'})
    def put(s, url, **kw):
        s.put_n += 1; cr = kw['headers'].get('Content-Range')
        s.calls.append(('PUT', cr))
        if s.put_n == 1: return R(503, {})
        if cr.startswith('bytes */'): return R(308, None, {'Range': 'bytes=0-9'})
        if s.put_n == 3: return R(308, None, {'Range': 'bytes=0-19'})
        return R(200, {'id': 'VID123', 'status': {'privacyStatus': 'private'}})

def test_upload_resume(monkeypatch):
    for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'): monkeypatch.setenv(k, 'x')
    monkeypatch.setattr(youtube, 'CHUNK', 10); monkeypatch.setattr(youtube, '_backoff', lambda a: None)
    f = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); f.write(b'0123456789' * 3); f.close()
    s = FakeSession()
    res = youtube.YouTube(s).upload(f.name, dict(title='t', publish_at='2026-11-13T16:30:00Z'), log=lambda *a: None)
    assert res['id'] == 'VID123'
    puts = [c[1] for c in s.calls if c[0] == 'PUT']
    assert puts == ['bytes 0-9/30', 'bytes */30', 'bytes 10-19/30', 'bytes 20-29/30'], puts

def test_auth_expired(monkeypatch):
    for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'): monkeypatch.setenv(k, 'x')
    class S:
        def post(s, *a, **k): return R(400, {'error': 'invalid_grant'})
    try:
        youtube.YouTube(S()).token(); assert False
    except youtube.AuthExpired: pass

def test_slots():
    cfg = json.load(open(publisher.CFG))
    tz = publisher.ZoneInfo(cfg['timezone'])

    def utc(day, hhmm):
        hh, mm = map(int, hhmm.split(':'))
        return dt.datetime(2026, 11, day, hh, mm, tzinfo=tz).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    S, L = cfg['short_slots_local'], cfg['long_slots_local']
    now = dt.datetime(2026, 11, 11, 23, 30, tzinfo=tz)            # after every slot of the day
    a = publisher.next_slot(cfg, {}, 'short', now)
    assert a == utc(12, S[0]), a
    b = publisher.next_slot(cfg, {'x': {'publish_at': a}}, 'short', now)
    assert b == utc(12, S[1]), b
    assert publisher.next_slot(cfg, {}, 'long', now) == utc(12, L[0])
    # a slot later the same day is used only when it is more than 30 minutes away
    hh, mm = map(int, S[-1].split(':'))
    last = dt.datetime(2026, 11, 11, hh, mm, tzinfo=tz)
    assert publisher.next_slot(cfg, {}, 'short', last - dt.timedelta(minutes=45)) == utc(11, S[-1])
    assert publisher.next_slot(cfg, {}, 'short', last - dt.timedelta(minutes=10)) == utc(12, S[0])
    # a full day of uploads never shares a time
    led = {}
    for i in range(len(S)):
        led['s%d' % i] = {'publish_at': publisher.next_slot(cfg, led, 'short', now)}
    for i in range(len(L)):
        led['l%d' % i] = {'publish_at': publisher.next_slot(cfg, led, 'long', now)}
    times = [v['publish_at'] for v in led.values()]
    assert len(set(times)) == len(S) + len(L), times


def test_plan_skips_uploaded():
    cfg = json.load(open(publisher.CFG))
    ids = [e['id'] for e in publisher.episodes() if e.get('status') in ('ready', 'approved')]
    assert publisher.plan(cfg, {i: {} for i in ids}) == []
