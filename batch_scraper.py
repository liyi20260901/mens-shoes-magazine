#!/usr/bin/env python3
"""
男鞋时尚电子杂志 - 批量抓取脚本
支持14个Shopify品牌，输出标准化JSON
"""

import requests
import json
import os
import time
import base64
from bs4 import BeautifulSoup

# ===== 品牌配置列表 =====
BRANDS_CONFIG = [{'name': 'Thursday Boots', 'url': 'https://thursdayboots.com', 'collection': '/collections/all'}, {'name': 'Oak Street Bootmakers', 'url': 'https://oakstreetbootmakers.com', 'collection': '/collections/all'}, {'name': 'Quoddy', 'url': 'https://quoddy.com', 'collection': '/collections/all'}, {'name': 'Beckett Simonon', 'url': 'https://beckettsimonon.com', 'collection': '/collections/all'}, {'name': 'Helm Boots', 'url': 'https://helmboots.com', 'collection': '/collections/all'}, {'name': 'Tecovas', 'url': 'https://tecovas.com', 'collection': '/collections/all'}, {'name': 'Frye', 'url': 'https://thefryecompany.com', 'collection': '/collections/all'}, {'name': 'Ariat', 'url': 'https://ariat.com', 'collection': '/collections/all'}, {'name': 'G.H. Bass', 'url': 'https://ghbass.com', 'collection': '/collections/all'}, {'name': "White's Boots", 'url': 'https://whitesboots.com', 'collection': '/collections/all'}, {'name': 'Truman Boot Co.', 'url': 'https://trumanboot.com', 'collection': '/collections/all'}, {'name': 'Keen Utility', 'url': 'https://keenfootwear.com', 'collection': '/collections/all'}, {'name': 'Dan Post', 'url': 'https://danpostboots.com', 'collection': '/collections/all'}, {'name': 'Lucchese', 'url': 'https://lucchese.com', 'collection': '/collections/all'}]

class ShopifyScraper:
    def __init__(self, brand_name, base_url, output_dir='./output'):
        self.brand_name = brand_name
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.products = []
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f'{output_dir}/images', exist_ok=True)

    def fetch_collection(self, collection_path='/collections/all'):
        """抓取产品列表页，提取Shopify内联JSON数据"""
        url = f'{self.base_url}{collection_path}'
        print(f'\n🔍 [{self.brand_name}] Fetching: {url}')

        try:
            resp = requests.get(url, headers=self.headers, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f'❌ Failed to fetch {url}: {e}')
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and '"collection"' in script.string and '"products"' in script.string:
                try:
                    start = script.string.find('{')
                    end = script.string.rfind('}') + 1
                    data = json.loads(script.string[start:end])
                    if 'collection' in data and 'products' in data['collection']:
                        products = data['collection']['products']
                        print(f'✅ Found {len(products)} products in JSON')
                        return products
                except:
                    pass

        print('⚠️ No Shopify JSON found, trying alternative methods...')
        return []

    def filter_shoes(self, products, keywords=None):
        """筛选鞋类产品，排除包/配饰"""
        if keywords is None:
            keywords = ['boot', 'shoe', 'loafer', 'oxford', 'derby', 'chukka', 
                       'chelsea', 'moccasin', 'slipper']

        shoe_products = []
        for p in products:
            title = p.get('title', '').lower()
            ptype = p.get('type', '').lower()
            if any(kw in ptype for kw in keywords) or any(kw in title for kw in keywords):
                shoe_products.append(p)

        print(f'👞 Filtered {len(shoe_products)} shoe products')
        return shoe_products

    def standardize(self, products, max_products=10):
        """标准化并输出JSON（不包含图片下载，仅URL）"""
        standardized = []
        for i, p in enumerate(products[:max_products]):
            image_src = p.get('image', {}).get('src', '')
            image_url = 'https:' + image_src if image_src.startswith('//') else image_src

            # 图片URL处理：添加尺寸参数优化加载
            if 'cdn.shopify.com' in image_url:
                image_url += '?v=' + str(int(time.time()))  # 避免缓存

            standardized.append({
                'brand': self.brand_name,
                'name': p.get('title', ''),
                'price': p.get('price', 0) / 100,
                'sale_price': None,
                'currency': 'USD',
                'image_url': image_url,
                'description': f"{p.get('type', 'Shoes').title()} - Premium construction",
                'materials': ['Leather', 'Handcrafted'],
                'product_url': f'{self.base_url}{p.get("url", "")}'
            })

        return standardized

    def scrape(self, max_products=10, collection_path='/collections/all'):
        """完整抓取流程"""
        print(f'\n🚀 [{self.brand_name}] Starting scrape...')

        raw_products = self.fetch_collection(collection_path)
        if not raw_products:
            print(f'⚠️ [{self.brand_name}] No products found')
            return None

        shoe_products = self.filter_shoes(raw_products)
        if not shoe_products:
            print(f'⚠️ [{self.brand_name}] No shoe products found')
            return None

        self.products = self.standardize(shoe_products, max_products)

        output = {
            'issue_date': time.strftime('%Y-%m-%d'),
            'theme': f'本周{self.brand_name}精选',
            'featured_brand': self.brand_name,
            'products': self.products
        }

        json_path = f'{self.output_dir}/{self.brand_name.lower().replace(" ", "_").replace(".", "_")}_products.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f'✅ Saved to {json_path} ({len(self.products)} products)')
        return output


def batch_scrape_all():
    """批量抓取所有配置品牌"""
    results = []
    for brand in BRANDS_CONFIG:
        scraper = ShopifyScraper(brand['name'], brand['url'])
        try:
            result = scraper.scrape(max_products=10, collection_path=brand['collection'])
            if result:
                results.append(result)
            time.sleep(3)  # 礼貌延迟
        except Exception as e:
            print(f'❌ Error scraping {brand["name"]}: {e}')

    # 保存汇总
    summary = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_brands': len(results),
        'total_products': sum(len(r['products']) for r in results),
        'brands': results
    }

    with open('./output/all_brands_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f'\n🎉 Batch complete! {len(results)}/{len(BRANDS_CONFIG)} brands scraped.')
    print(f'📊 Total products: {summary["total_products"]}')
    return results


if __name__ == '__main__':
    batch_scrape_all()
