import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup

st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

# 美化 UI
st.markdown("""
    <style>
    .product-box { border: 1px solid #eee; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center; background: white; color: black; }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 1.3rem; margin: 10px 0; }
    img { border-radius: 8px; width: 100%; height: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 實時清單")

def fetch_data():
    url = "https://www.freitag.ch/en/f306"
    # 使用 cloudscraper 繞過 Cloudflare 等防爬工具
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200:
            st.error(f"網站回傳錯誤碼: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 尋找產品容器
        items = soup.select('li.product-item')
        
        for item in items:
            try:
                # 抓取圖片
                img_tag = item.select_one('img.product-image-photo')
                img_url = img_tag.get('data-src') or img_tag.get('src')
                
                # 抓取連結
                link_tag = item.select_one('a.product-item-link')
                link = link_tag['href'] if link_tag else url
                
                # 抓取價格
                price_tag = item.select_one('.price')
                price = price_tag.get_text().strip() if price_tag else "See Price"
                
                if img_url and "placeholder" not in img_url:
                    products.append({"img": img_url, "price": price, "link": link})
            except:
                continue
        return products
    except Exception as e:
        st.error(f"連線發生異常: {e}")
        return []

if st.button('🚀 點擊刷新最新庫存'):
    with st.spinner('正在突破官網防火牆並搬運數據...'):
        data = fetch_data()
        if data:
            st.success(f"成功！目前有 {len(data)} 款 F306 現貨")
            for p in data:
                with st.container():
                    st.markdown(f"""
                    <div class="product-box">
                        <img src="{p['img']}">
                        <div class="price-text">{p['price']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("👉 前往官網下單", p['link'])
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("還是沒抓到資料。官網可能開啟了更高級的防護。請稍等幾分鐘後再次嘗試。")
