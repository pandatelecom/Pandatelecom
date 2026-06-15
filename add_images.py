import re

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-data.js', 'r') as f:
    txt = f.read()

# Extract SKU + name pairs from products-data.js
products = re.findall(r"\{cat:'[^']*',sku:'([^']*)',name:'([^']*)',", txt)

# Build image map using Momax CDN pattern
# Pattern discovered: https://hk.momax.net/cdn/shop/products/{SKU}_01_1500.png
img_map_lines = []
img_map_lines.append('const IMG = {')
for sku, name in products[:80]:  # First 80 products
    if sku:
        url = f"  '{sku}': 'https://hk.momax.net/cdn/shop/products/{sku}_01_1500.png'"
        img_map_lines.append(url)
img_map_lines.append('};')

# Read the current selfcontained HTML
with open('/tmp/products_selfcontained.html', 'r') as f:
    html = f.read()

# Find where to inject the IMG map (before the first script)
# Replace the existing render function to use IMG map
old_render = '''function render(q,cat){q=(q||'').toLowerCase().trim();cat=cat||'';let out='',has=false;DATA.cats'''

new_render = '''const IMG_MAP = {};
''' + '\n'.join(img_map_lines) + '''

function render(q,cat){q=(q||'').toLowerCase().trim();cat=cat||'';let out='',has=false;DATA.cats'''

html = html.replace(old_render, new_render)

# Update the card rendering to include images
old_card = '''<div class="card-thumb">📦</div>'''
new_card = '''<div class="card-thumb"><img src="${IMG_MAP[p.sku] || ''}" alt="${p.name}" loading="lazy" onerror="this.style.display='none';this.parentNode.innerHTML='📦'" /></div>'''

html = html.replace(old_card, new_card)

# Save updated version
with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'w') as f:
    f.write(html)

print('Updated products-selfcontained.html with images')
print(f'Added {min(80, len(products))} image URLs')
