import streamlit as st
import requests

st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

st.markdown("""
    <style>
    .product-box { border: 1px solid #eee; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center; background: white; color: black; }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 1.3rem; margin: 10px 0; }
    img { border-radius: 8px; width: 100%; height: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 掃描器")
st.caption("直接抓取 Freitag 官方產品目錄數據")

def fetch_data():
    # 這是 Freitag 官方最直接的產品列表數據接口 (F306 型號代碼 2211)
    # 我們改用更通用的請求方式
    url = "https://www.freitag.ch/en/f306/load-more"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    try:
        # 直接請求 load-more 介面，這通常會回傳當前所有庫存的 HTML 或是 JSON
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # 定位所有產品項目
            items = soup.select('.product-item')
            for item in items:
                try:
                    img_tag = item.select_one('img')
                    # 抓取圖片，優先找延遲載入的真實位址
                    img = img_tag.get('data-src') or img_tag.get('src')
                    if img and img.startswith('/'):
                        img = "https://www.freitag.ch" + img
                        
                    price = item.select_one('.price').get_text().strip()
                    link = "https://www.freitag.ch" + item.select_one('a')['href']
                    
                    if "placeholder" not in img:
                        products.append({"img": img, "price": price, "link": link})
                except:
                    continue
            return products
        else:
            st.error(f"官網回應異常 (代碼: {response.status_code})")
            return []
    except Exception as e:
        st.error(f"連線失敗: {e}")
