"""
Auto-discover Shopify/Momax product image URLs and map them to SKUs.
Strategy:
  1. Shopify JSON product feed -> cdn.shopify.com/s/files/... images
  2. HK Momax CDN -> product page scrape when available
"""
import json, re, sys, os
from pathlib import Path
import urllib.request, ssl

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

products_html = Path("/Users/panda/.openclaw/workspace/panda-telecom/products.html").read_text()
products_js = Path("/Users/panda/.openclaw/workspace/panda-telecom/products-data.js").read_text()

# Extract current IMG map from products.html
img_line_re = re.search(r'const IMG = \{(.+?)\};', products_html, re.DOTALL)
current_img = {}
if img_line_re:
    img_line = img_line_re.group(1)
    for m in re.finditer(r'"([^"]+)":\s*"([^"]+)"', img_line):
        current_img[m.group(1)] = m.group(2)

# Extract SKU->name from products-data.js with regex (JS uses unquoted keys + single quotes)
sku_name_re = re.compile(r"\{[^}]*sku:'([^']*)'[^}]*name:'([^']*)'[^}]*\}")
product_entries = sku_name_re.findall(products_js)
all_skus = set()
sku_to_name = {}
for sku, name in product_entries:
    if sku:
        all_skus.add(sku)
        sku_to_name[sku] = name

missing_skus = sorted([s for s in all_skus if s not in current_img])
print(f'Total SKUs with sku: {len(all_skus)}, already have images: {len(current_img)}, still need: {len(missing_skus)}')
if missing_skus:
    print('Still needing images (sample:', missing_skus[:10], '...)')

def http_get(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; image-bot/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def page_images(url):
    html = http_get(url)
    if not html:
        return []
    imgs = []
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
    if m:
        imgs.append(m.group(1))
    m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html)
    if m:
        imgs.append(m.group(1))
    imgs += re.findall(r'https://cdn\.shopify\.com/s/files/1/0800/4727/6344/[^"\']+\.(?:png|jpg|webp)', html)
    seen = set(); out = []
    for x in imgs:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

new_entries = {}

# Shopify products.json
for page in range(1, 15):
    url = f'https://cdn.shopify.com/s/files/1/0800/4727/6344/products.json?limit=250&page={page}'
    txt = http_get(url)
    if not txt:
        break
    try:
        j = json.loads(txt)
        prod_list = j.get('products', [])
    except Exception:
        break
    if not prod_list:
        break
    for prod in prod_list:
        title = prod.get('title', '')
        handle = prod.get('handle', '')
        matched_sku = None
        for sku, name in sku_to_name.items():
            if sku in current_img:
                continue
            tokens_sku = re.findall(r'[A-Z0-9]{3,}', sku)
            if sku.lower() in title.lower() or handle.lower() in title.lower() or any(t.lower() in title.lower() for t in tokens_sku):
                matched_sku = sku
                break
        if not matched_sku:
            continue
        img = prod.get('image')
        if isinstance(img, dict) and 'src' in img:
            new_entries.setdefault(matched_sku, img['src'])

# HK momax collection pages
hk_url = 'https://hk.momax.net/collections/all'
html = http_get(hk_url)
if html:
    links = re.findall(r'href="(/products/[^"]+)"', html)
    handles = []
    seen_h = set()
    for l in links:
        h = l.strip('/')
        if h in ('products', 'all') or h in seen_h:
            continue
        seen_h.add(h); handles.append(h)
    print(f'Found {len(handles)} product handles on hk.momax.net collections/all')
    for h in handles:
        matched_sku = None
        for sku, name in sku_to_name.items():
            if sku in current_img:
                continue
            tokens_sku = re.findall(r'[A-Z0-9]{3,}', sku)
            if any(t.lower() in h.lower() for t in tokens_sku):
                matched_sku = sku
                break
        if not matched_sku:
            continue
        imgs = page_images(f'https://hk.momax.net/products/{h}')
        if imgs:
            new_entries.setdefault(matched_sku, imgs[0])

print(f'Discovered {len(new_entries)} new entries; after adding total would be {len(current_img)+len(new_entries)}')
Path('/tmp/new_img_map.json').write_text(json.dumps(new_entries, ensure_ascii=False, indent=2))
print('Wrote /tmp/new_img_map.json with discovered URLs')
