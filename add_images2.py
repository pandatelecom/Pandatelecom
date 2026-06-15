import re

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-data.js', 'r') as f:
    txt = f.read()

# Extract SKU + name pairs from products-data.js
products = re.findall(r"\{cat:'[^']*',\s*sku:'([^']*)',\s*name:'([^']*)',", txt)

print(f'Found {len(products)} products')

img_map_lines = ['const IMG = {']
for sku, name in products:
    if sku:
        url = f"  '{sku}': 'https://hk.momax.net/cdn/shop/products/{sku}_01_1500.png'"
        img_map_lines.append(url)
img_map_lines.append('};')

with open('/tmp/products_selfcontained.html', 'r') as f:
    html = f.read()

# Inject IMG_MAP before first script
html = html.replace('<script>', '\n'.join(img_map_lines) + '\n<script>', 1)

# Update render function
old_render = 'function render(q,cat){'
new_render = ('const IMG_MAP = {};\n' + '\n'.join(img_map_lines) + '\n\nfunction render(q,cat){')
html = html.replace('function render(q,cat){', new_render)

# Update card to use IMG_MAP
old_card = """<div class="card-thumb">📦</div>"""
new_card = """<div class="card-thumb"><img src="${IMG[p.sku] || ''}" alt="${p.name}" loading="lazy" onerror="this.style.opacity='0'" /></div>"""
html = html.replace(old_card, new_card)

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'w') as f:
    f.write(html)

print('Done updating')
