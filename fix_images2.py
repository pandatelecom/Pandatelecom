import re

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-data.js', 'r') as f:
    txt = f.read()

products = re.findall(r"\{cat:'[^']*',\s*sku:'([^']*)',\s*name:'([^']*)',", txt)
print(f'Found {len(products)} products')

def base_model(sku):
    if not sku:
        return ''
    m = re.match(r'^([A-Z]{1,3}\d+[A-Z0-9]*)', sku)
    return m.group(1) if m else sku

img_map = {}
for sku, name in products:
    if not sku:
        continue
    b = base_model(sku)
    url = f'https://hk.momax.net/cdn/shop/products/{b}_01_1500.png?v=1'
    img_map[sku] = url

print(f'Generated {len(img_map)} image URLs')
print('Sample:', list(img_map.items())[:5])

# Inject into selfcontained HTML
with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'r') as f:
    html = f.read()

img_lines = ['const IMG = {']
for sku, url in img_map.items():
    img_lines.append(f"  '{sku}': '{url}',")
img_lines.append('};')

html = html.replace('<script>', '\n'.join(img_lines) + '\n<script>', 1)

old_card = """<div class="card-thumb">📦</div>"""
new_card = """<div class="card-thumb"><img src="${IMG[p.sku] || ''}" alt="${p.name}" loading="lazy" onerror="this.parentNode.innerHTML='📦'" /></div>"""
html = html.replace(old_card, new_card)

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'w') as f:
    f.write(html)

# copy to desktop
import shutil
shutil.copy('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', '/Users/panda/Desktop/products-selfcontained.html')
print('Done')
