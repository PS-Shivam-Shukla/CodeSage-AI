import urllib.request
import urllib.error

urls = [
    'http://127.0.0.1:5174/',
    'http://127.0.0.1:8000/index/status',
    'http://127.0.0.1:8000/index',
]
for url in urls:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as r:
            print(url, 'OK', r.status)
            print('ACAO:', r.headers.get('Access-Control-Allow-Origin'))
            data = r.read(200).decode('utf-8', errors='replace')
            print(data[:500])
    except urllib.error.HTTPError as e:
        print(url, 'HTTPERR', e.code, e.reason)
        print(e.headers)
    except urllib.error.URLError as e:
        print(url, 'URLERR', e.reason)
    except Exception as e:
        print(url, 'ERR', type(e).__name__, e)
