import urllib.request

urls = [
    'https://a.tile.openstreetmap.org/7/96/56.png',
    'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/7/56/96'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        res = urllib.request.urlopen(req)
        print(f"{u} -> STATUS {res.status}, Content-Type: {res.headers.get('Content-Type')}")
    except Exception as e:
        print(f"{u} -> FAILED: {e}")
