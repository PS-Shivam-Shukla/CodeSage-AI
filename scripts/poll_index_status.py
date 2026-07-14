import time
import urllib.request
import json

url = 'http://127.0.0.1:8000/index/status'

end = time.time() + 120
while time.time() < end:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
            print('status:', data)
            if data.get('embeddings', 0) > 0:
                print('Embeddings present — indexing appears complete.')
                break
    except Exception as e:
        print('error:', e)
    time.sleep(5)
else:
    print('Timed out waiting for embeddings > 0')
