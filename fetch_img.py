import urllib.request, ssl, re, json, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

skus = ['IP117D','AP12UKW','BS6HKD','BT13D','CM22E','DC35D','UA10UKD','UM76UKD','IF15W','IF16UKW','IP115D','IP130B']

def try_image(sku):
    patterns = []
    for variant in ['01_1500', '01', '_1', '']:
        patterns += [
            f'https://hk.momax.net/cdn/shop/products/{sku}_{variant}.png?v=1',
            f'https://hk.momax.net/cdn/shop/products/{sku.lower()}_{variant}.png?v=1',
            f'https://hk.momax.net/cdn/shop/files/{sku}_{variant}.png?v=1',
            f'https://hk.momax.net/cdn/shop/files/{sku.lower()}_{variant}.webp?v=1',
        ]
    for url in patterns:
        try:
            req = urllib.request.Request(url, method='HEAD', headers={'User-Agent':'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=3, context=ctx)
            if resp.status == 200:
                return url
        except Exception:
            pass
    return None

results = {}
for sku in skus:
    url = try_image(sku)
    results[sku] = url
    print(f'{sku}: {url or "NOT FOUND"}')
    time.sleep(0.1)

with open('/Users/panda/.openclaw/workspace/panda-telecom/sku_images.json','w') as f:
    json.dump(results, f, indent=2)
print('Saved sku_images.json')
