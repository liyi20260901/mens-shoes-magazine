#!/usr/bin/env python3
"""
自动生成杂志HTML - GitHub Actions用
读取output目录下的品牌JSON，生成一期完整杂志
"""

import json
import os
import glob
from datetime import datetime

def generate_magazine():
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有品牌JSON文件
    json_files = glob.glob(f'{output_dir}/*_products.json')
    if not json_files:
        print("⚠️ No product data found, generating demo issue")
        return generate_demo_issue()
    
    # 读取所有品牌数据
    all_brands = []
    for jf in json_files:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_brands.append(data)
    
    # 选择本期主打品牌（轮询制）
    issue_number = datetime.now().timetuple().tm_yday  # 用一年中的第几天作为期号
    featured_idx = issue_number % len(all_brands)
    featured = all_brands[featured_idx]
    
    # 生成HTML
    html = build_html(featured, issue_number, len(all_brands))
    
    # 保存主文件（GitHub Pages入口）
    html_path = f'{output_dir}/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 同时保存历史版本
    today = datetime.now().strftime('%Y%m%d')
    history_path = f'{output_dir}/issue_{today}.html'
    with open(history_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated: {html_path}")
    print(f"✅ History: {history_path}")
    return html_path

def generate_demo_issue():
    """没有数据时生成demo"""
    demo_data = {
        'issue_date': datetime.now().strftime('%Y-%m-%d'),
        'theme': '本周工装靴精选',
        'featured_brand': 'Thursday Boots',
        'products': [
            {
                'brand': 'Thursday Boots',
                'name': 'Captain Boot',
                'price': 199.00,
                'currency': 'USD',
                'image_url': 'https://cdn.shopify.com/s/files/1/0460/2180/8450/products/Captain_Arizona_Adobe_01.jpg',
                'description': '经典6寸工装靴，全粒面皮革',
                'materials': ['全粒面皮革', '固特异沿条'],
                'product_url': 'https://thursdayboots.com/products/captain'
            }
        ]
    }
    return build_html(demo_data, 1, 1)

def build_html(data, issue_num, total_brands):
    """构建杂志HTML"""
    products = data['products']
    brand = data['featured_brand']
    theme = data['theme']
    date = data['issue_date']
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>SNEAKER DIGEST | {theme}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
:root {{ --deep-brown: #3D2314; --navy: #1B2A4A; --ivory: #F5F0E8; --gold: #C9A962; --cream: #FAF7F2; --text-dark: #2C1810; --text-light: #8B7355; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--cream); color: var(--text-dark); overflow-x: hidden; }}
.magazine {{ display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; scrollbar-width: none; height: 100vh; }}
.magazine::-webkit-scrollbar {{ display: none; }}
.page {{ flex: 0 0 100vw; width: 100vw; height: 100vh; scroll-snap-align: start; overflow-y: auto; position: relative; }}
.cover {{ display: flex; flex-direction: column; justify-content: center; align-items: center; background: linear-gradient(135deg, var(--deep-brown) 0%, var(--navy) 100%); color: var(--ivory); text-align: center; padding: 2rem; }}
.cover-badge {{ font-size: 0.65rem; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); margin-bottom: 1.5rem; border: 1px solid var(--gold); padding: 0.4rem 1rem; display: inline-block; }}
.cover h1 {{ font-family: 'Playfair Display', serif; font-size: 2.8rem; font-weight: 700; line-height: 1.1; margin-bottom: 1rem; letter-spacing: -1px; }}
.cover-subtitle {{ font-size: 1rem; font-weight: 300; color: rgba(245,240,232,0.8); margin-bottom: 2rem; }}
.cover-date {{ font-size: 0.75rem; letter-spacing: 3px; color: var(--gold); text-transform: uppercase; }}
.product-page {{ display: flex; flex-direction: column; padding: 0; background: var(--cream); }}
.product-card {{ flex: 1; display: flex; flex-direction: column; padding: 0 1.5rem 2rem; }}
.product-image-wrapper {{ position: relative; width: 100%; padding-bottom: 100%; background: linear-gradient(145deg, var(--ivory) 0%, #EDE8E0 100%); border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem; }}
.product-image {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; padding: 1rem; }}
.product-tag {{ position: absolute; top: 1rem; left: 1rem; background: var(--deep-brown); color: var(--ivory); font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase; padding: 0.3rem 0.8rem; border-radius: 2px; }}
.product-info {{ text-align: center; }}
.product-name {{ font-family: 'Playfair Display', serif; font-size: 1.3rem; color: var(--text-dark); margin-bottom: 0.5rem; line-height: 1.3; }}
.product-price {{ font-size: 1.1rem; font-weight: 600; color: var(--deep-brown); margin-bottom: 0.8rem; }}
.product-price .currency {{ font-size: 0.8rem; font-weight: 400; color: var(--text-light); }}
.product-desc {{ font-size: 0.8rem; color: var(--text-light); line-height: 1.6; margin-bottom: 1rem; }}
.product-materials {{ display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
.material-tag {{ font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; color: var(--text-light); border: 1px solid #D4C9B8; padding: 0.25rem 0.6rem; border-radius: 2px; }}
.cta-button {{ display: inline-block; background: var(--deep-brown); color: var(--ivory); font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; padding: 0.9rem 2rem; border-radius: 2px; text-decoration: none; }}
.trend-page {{ display: flex; flex-direction: column; justify-content: center; padding: 3rem 1.5rem; background: linear-gradient(135deg, var(--navy) 0%, var(--deep-brown) 100%); color: var(--ivory); }}
.trend-title {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; margin-bottom: 2rem; text-align: center; }}
.trend-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
.stat-item {{ text-align: center; padding: 1rem; border: 1px solid rgba(201,169,98,0.3); border-radius: 8px; }}
.stat-number {{ font-family: 'Playfair Display', serif; font-size: 2rem; color: var(--gold); display: block; }}
.stat-label {{ font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; color: rgba(245,240,232,0.7); }}
.share-page {{ display: flex; flex-direction: column; justify-content: center; padding: 3rem 1.5rem; text-align: center; background: var(--cream); }}
.share-title {{ font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--deep-brown); margin-bottom: 1rem; }}
.share-text {{ font-size: 0.85rem; color: var(--text-light); margin-bottom: 2rem; line-height: 1.6; }}
.pagination {{ display: flex; justify-content: center; gap: 0.4rem; padding: 1rem; position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; background: linear-gradient(to top, rgba(250,247,242,0.9), transparent); }}
.dot {{ width: 6px; height: 6px; border-radius: 50%; background: rgba(61,35,20,0.2); transition: all 0.3s; }}
.dot.active {{ background: var(--deep-brown); width: 18px; border-radius: 3px; }}
.hint {{ position: fixed; top: 1rem; right: 1rem; font-size: 0.65rem; color: rgba(61,35,20,0.4); z-index: 100; letter-spacing: 1px; }}
</style>
</head>
<body>
<div class="hint">← 左右滑动浏览 →</div>
<div class="magazine" id="magazine">
'''
    
    # 封面
    html += f'''
  <div class="page cover">
    <div class="cover-badge">Weekly Selection · {total_brands} Brands</div>
    <h1>{brand.replace(" ", "<br>")}</h1>
    <p class="cover-subtitle">{theme}</p>
    <p class="cover-date">{date} · ISSUE {issue_num:03d}</p>
  </div>
'''
    
    # 产品页
    for i, p in enumerate(products):
        materials = ''.join([f'<span class="material-tag">{m}</span>' for m in p['materials']])
        html += f'''
  <div class="page product-page">
    <div class="product-card">
      <div class="product-image-wrapper">
        <img src="{p['image_url']}" alt="{p['name']}" class="product-image" loading="lazy">
        <span class="product-tag">{p['brand']}</span>
      </div>
      <div class="product-info">
        <h3 class="product-name">{p['name']}</h3>
        <p class="product-price"><span class="currency">{p['currency']}</span> ${p['price']:.2f}</p>
        <p class="product-desc">{p['description']}</p>
        <div class="product-materials">{materials}</div>
        <a href="{p['product_url']}" class="cta-button" target="_blank">查看官网</a>
      </div>
    </div>
  </div>
'''
    
    # 趋势页
    avg_price = sum(p['price'] for p in products) / len(products) if products else 0
    html += f'''
  <div class="page trend-page">
    <h2 class="trend-title">本期数据</h2>
    <div class="trend-stats">
      <div class="stat-item">
        <span class="stat-number">{len(products)}</span>
        <span class="stat-label">精选鞋款</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">${avg_price:.0f}</span>
        <span class="stat-label">均价</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">100%</span>
        <span class="stat-label">皮革材质</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{total_brands}</span>
        <span class="stat-label">合作品牌</span>
      </div>
    </div>
  </div>
'''
    
    # 分享页
    html += f'''
  <div class="page share-page">
    <h2 class="share-title">分享给同事</h2>
    <p class="share-text">觉得这本杂志有用？<br>转发给对男鞋感兴趣的同事</p>
    <a href="#" class="cta-button" onclick="navigator.clipboard.writeText(window.location.href);alert('链接已复制');return false;">复制链接</a>
  </div>
</div>
<div class="pagination" id="pagination">
  <div class="dot active"></div>
  <div class="dot"></div>
  {''.join(['<div class="dot"></div>' for _ in range(len(products) + 1)])}
</div>
<script>
const magazine = document.getElementById('magazine');
const dots = document.querySelectorAll('.dot');
magazine.addEventListener('scroll', () => {{
  const currentPage = Math.round(magazine.scrollLeft / window.innerWidth);
  dots.forEach((dot, index) => {{ dot.classList.toggle('active', index === currentPage); }});
}});
</script>
</body>
</html>'''
    
    return html

if __name__ == '__main__':
    generate_magazine()
