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
    now = dt.datetime(2026, 11, 11, 22, 0, tzinfo=tz)
    a = publisher.next_slot(cfg, {}, 'short', now)
    assert a == '2026-11-12T16:30:00Z', a
    b = publisher.next_slot(cfg, {'x': {'publish_at': a}}, 'short', now)
    assert b == '2026-11-12T21:30:00Z', b
    l = publisher.next_slot(cfg, {}, 'long', now)
    assert l == '2026-11-14T17:00:00Z', l  # Sat 12:00 EST
