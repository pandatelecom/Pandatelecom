import re, json

# current IMG map from HTML
with open('products.html') as f:
    html = f.read()

m = re.search(r'const IMG = ({.*?});', html, re.DOTALL)
img_map = eval(m.group(1))
print('Existing IMG map size:', len(img_map))

# Shopify products.json fetched main product URLs mapped to SKUs
shopify_map = {
 "BR10AGSB": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/BR10AGS_B_01_1500.webp?v=1779163706",
 "BR10AGSR": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/BR10AGS_R_01_1500.webp?v=1779163706",
 "BR10AGSG": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/BR10AGS_G_01_1500.webp?v=1779163706",
 "BR10AGSP": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/BR10AGS_P_01_1500.webp?v=1779163705",
 "IP179D": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP179_D_01_1500.webp?v=1779849507",
 "IP179W": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP179_W_01_1500.webp?v=1779849507",
 "IP179B": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP179_B_01_1500.webp?v=1779849507",
 "IP178D": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP178_D_01_1500.webp?v=1779848541",
 "IP178W": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP178_W_01_1500.webp?v=1779848541",
 "IP178B": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP178_B_01_1500.webp?v=1779848541",
 "WJCJIPL": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/WJCIP_02_1500.jpg?v=1780986809",
 "WJCJIPD": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/WJCIP_01_1500.jpg?v=1780986809",
 "IP175HKL": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP175HK_L_01_1500.jpg?v=1778559854",
 "IP175HKD": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/IP175HK_D_01_1500.jpg?v=1778559843",
 # existing overriding untouched
 "MS02L2": "https://cdn.shopify.com/s/files/1/0800/4727/6344/files/MS02_L2_01_1500_Additional_JPG_Medium_a0e638c5-d5f5-49ec-a129-fc0fc48aede4.jpg?v=1742745828",
}

# add shopify main page only first page, then second page? but we only have page 1; later may need append.
# For now add only unique SKUs still missing and present in vendor fetch.
added=[]
for sku, url in shopify_map.items():
    if sku not in img_map:
        img_map[sku] = url
        added.append(sku)

print('Added this run:', len(added))
print('Updated IMG map size:', len(img_map))

# Write back IMG map to HTML
# Find start and end of object
start = html.index('const IMG = {')
end = html.index('};', start) + 2
obj_str = json.dumps(img_map, ensure_ascii=False)
new_html = html[:start] + 'const IMG = ' + obj_str + ';' + html[end:]
with open('products.html', 'w') as f:
    f.write(new_html)
print('products.html updated')
