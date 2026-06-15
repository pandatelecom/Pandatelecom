import re

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-data.js', 'r') as f:
    txt = f.read()

products = re.findall(r"\{cat:'[^']*',\s*sku:'([^']*)',\s*name:'([^']*)',", txt)
print(f'Found {len(products)} products')

def base_model(sku):
    if not sku:
        return ''
    m = re.match(r'^([A-Z]{1,3}\d+)', sku)
    return m.group(1) if m else sku

# Use Shopify CDN pattern that we KNOW works
img_map = {}
for sku, name in products:
    if not sku:
        continue
    b = base_model(sku)
    # Use the working Shopify CDN pattern
    url = f'https://cdn.shopify.com/s/files/1/0800/4727/6344/products/{sku}_01_1500.png?v=1'
    img_map[sku] = url

print(f'Generated {len(img_map)} URLs')

# Read selfcontained html
with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'r') as f:
    html = f.read()

# Remove old IMG map
html = re.sub(r'const IMG = \{[^;]*\};\n', '', html)

# Inject new IMG map before first script
img_lines = ['const IMG = {']
for sku, url in img_map.items():
    img_lines.append(f"  '{sku}': '{url}',")
img_lines.append('};')

html = html.replace('<script>', '\n'.join(img_lines) + '\n<script>', 1)

# Keep card-thumb with img tag that falls back to 📦
# The onerror is already there

with open('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', 'w') as f:
    f.write(html)

# Copy to desktop
import shutil
shutil.copy('/Users/panda/.openclaw/workspace/panda-telecom/products-selfcontained.html', '/Users/panda/Desktop/products-selfcontained.html')
print('Done - saved to workspace and desktop')
