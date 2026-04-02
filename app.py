import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

st.markdown("""
    <style>
    .product-box { border: 1px solid #eee; border-radius: 10px; padding: 10px; margin-bottom: 15px; text-align: center; background: white; }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 1.2rem; margin: 10px 0; }
    img { border-radius: 8px; max-width: 100%; height: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 實時清單")

def fetch_data():
    # 使用 F306 的具體分類網址
    url = "https://www.freitag.ch/en/f306"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 修正後的定位邏輯：Freitag 現在常用 li.item.product-item 
        items = soup.find_all('li', class_='product-item')
        
        for item in items:
            try:
                # 抓取圖片 (嘗試多個屬性以防 lazy loading)
                img_tag = item.find('img')
                img_url = img_tag.get('data-src') or img_tag.get('src')
                
                # 抓取連結
                link_tag = item.find('a', class_='product-item-link')
                link = link_tag['href'] if link_tag else "https://www.freitag.ch/en/f306"
                
                # 抓取價格
                price_tag = item.find('span', class_='price')
                price = price_tag.get_text().strip() if price_tag else "Check Website"
                
                if img_url and "placeholder" not in img_url:
                    products.append({"img": img_url, "price": price, "link": link})
            except Exception:
                continue
        return products
    except Exception as e:
        st.error(f"連線出錯: {e}")
        return []

if st.button('🔄 點擊刷新最新庫存'):
    with st.spinner('正在從瑞士搬運數據...'):
        data = fetch_data()
        if data:
            st.success(f"找到 {len(data)} 款 F306！")
            for p in data:
                with st.container():
                    st.markdown(f"""
                    <div class="product-box">
                        <img src="{p['img']}">
                        <p class="price-text">{p['price']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("👉 前往購買", p['link'])
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("暫時沒抓到資料。原因可能是：1. 該型號剛好賣完 2. 官網正在反爬蟲。請稍後再試。")
