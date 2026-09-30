import urllib.request
import json

def test_get(url):
    try:
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        print(f"GET {url} -> STATUS {res.status}, SUCCESS: {data.get('success')}")
        return data
    except Exception as e:
        print(f"GET {url} FAILED: {e}")

def test_post(url, payload):
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        print(f"POST {url} -> STATUS {res.status}, SUCCESS: {data.get('success')}")
        return data
    except Exception as e:
        print(f"POST {url} FAILED: {e}")

if __name__ == '__main__':
    print("--- Testing CycloneShield AI REST API Endpoints ---")
    test_get('http://127.0.0.1:5000/api/health')
    test_get('http://127.0.0.1:5000/api/cyclones')
    test_get('http://127.0.0.1:5000/api/cyclones/amphan_2020')
    test_get('http://127.0.0.1:5000/api/infrastructure')
    test_get('http://127.0.0.1:5000/api/infrastructure/exposed?cyclone_id=amphan_2020&buffer_km=50.0')
    test_post('http://127.0.0.1:5000/api/forecast', {'cyclone_id': 'amphan_2020', 'buffer_km': 50.0})
    test_post('http://127.0.0.1:5000/api/simulation', {'cyclone_id': 'amphan_2020', 'delta_wind_knots': 10, 'delta_rainfall_percent': 20})
    test_get('http://127.0.0.1:5000/api/gee/layers')
    test_get('http://127.0.0.1:5000/api/gee/elevation')
    test_get('http://127.0.0.1:5000/api/gee/satellite')
    test_post('http://127.0.0.1:5000/api/ai/explain', {'cyclone_id': 'amphan_2020'})
    test_post('http://127.0.0.1:5000/api/ai/chat', {'query': 'Why is this area high risk?'})
    test_post('http://127.0.0.1:5000/api/ai/scenario-analysis', {'cyclone_id': 'amphan_2020'})
    test_post('http://127.0.0.1:5000/api/ai/advisory', {'cyclone_name': 'Amphan'})
