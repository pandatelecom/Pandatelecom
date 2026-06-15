import re, urllib.request, ssl, json, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-data.js', 'r') as f:
    txt = f.read()

products = re.findall(r"\{cat:'[^']*',\s*sku:'([^']*)',\s*name:'([^']*)',", txt)
print(f'Found {len(products)} products')

def guess_image_url(sku):
    if not sku:
        return ''
    # Try CDN product image first
    base = sku.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    if not base:
        base = sku
    # Keep last char if it could be color marker, but try base first
    candidates = [
        f'https://hk.momax.net/cdn/shop/products/{base}_01_1500.png?v=1',
        f'https://hk.momax.net/cdn/shop/products/{sku}_01_1500.png?v=1',
        f'https://hk.momax.net/cdn/shop/files/{base.lower()}.webp?v=1',
        f'https://hk.momax.net/cdn/shop/products/{base}.png',
        f'https://hk.momax.net/cdn/shop/products/{sku}.png',
    ]
    # Quick check first candidate only
    url = candidates[0]
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=3, context=ctx)
        if resp.status == 200:
            return url
    except:
        pass
    return ''

img_map = {}
missing = []
for sku, name in products:
    url = guess_image_url(sku)
    if url:
        img_map[sku] = url
    else:
        missing.append(sku)

print(f'Found images for {len(img_map)}/{len(products)}')
print('Missing samples:', missing[:10])

# Read selfcontained html
with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'r') as f:
    html = f.read()

# Inject img map before first script
img_lines = ['const IMG = {']
for sku, url in img_map.items():
    img_lines.append(f"  '{sku}': '{url}',")
img_lines.append('};')

html = html.replace('<script>', '\n'.join(img_lines) + '\n<script>', 1)

# Update card rendering
old_card = """<div class="card-thumb">📦</div>"""
new_card = """<div class="card-thumb"><img src="${IMG[p.sku] || ''}" alt="${p.name}" loading="lazy" onerror="this.parentNode.innerHTML='📦'" /></div>"""
html = html.replace(old_card, new_card)

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'w') as f:
    f.write(html)

print('Done - saved products-selfcontained.html')
