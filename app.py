import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="F306 掃描器", layout="centered")
st.title("🎒 F306 HAZZARD 掃描器")

def fetch_data():
    # 嘗試直接訪問「分類列表」的片段，通常這種 AJAX 接口防護較少
    url = "https://www.freitag.ch/en/f306/load-more" 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest", # 偽裝成網頁內部的 AJAX 請求
        "Accept": "text/html, */*; q=0.01"
    }
    
    try:
        # 第一步：嘗試抓取 load-more 片段
        response = requests.get(url, headers=headers, timeout=15)
        
        # 如果 load-more 失敗，嘗試回歸主頁
        if response.status_code != 200 or len(response.text) < 500:
            url = "https://www.freitag.ch/en/f306"
            response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 尋找所有帶有產品資訊的 <li> 或 <div>
        items = soup.select('.product-item') or soup.find_all(class_='item')
        
        for item in items:
            try:
                img_tag = item.find('img')
                if not img_tag: continue
                
                # 抓取圖片：嘗試所有潛在的屬性
                img = img_tag.get('data-src') or img_tag.get('src') or img_tag.get('data-original')
                
                if img and img.startswith('/'):
                    img = "https://www.freitag.ch" + img
                
                link_tag = item.find('a', href=True)
                link = "https://www.freitag.ch" + link_tag['href'] if link_tag else url
                
                price_tag = item.select_one('.price')
                price = price_tag.get_text().strip() if price_tag else "詳情請見官網"
                
                # 過濾掉一些無用的佔位圖
                if img and "placeholder" not in img and "gif" not in img:
                    products.append({"img": img, "price": price, "link": link})
            except:
                continue
        
        return products
    except Exception as e:
        return f"連線發生錯誤: {str(e)}"

if st.button('🚀 深度掃描最新現貨'):
    with st.spinner('正在與瑞士伺服器通訊...'):
        result = fetch_data()
        
        if isinstance(result, str):
            st.error(result)
        elif not result:
            st.warning("⚠️ 官網目前沒有顯示 F306 產品，或 Streamlit IP 已被暫時屏蔽。")
            st.info("💡 建議：可以嘗試在 10 分鐘後再次重新整理。")
        else:
            st.success(f"發現 {len(result)} 款產品！")
            # 建立兩列顯示，更像手機 App
            cols = st.columns(2)
            for idx, p in enumerate(result):
                with cols[idx % 2]:
                    st.image(p['img'], use_container_width=True)
                    st.write(f"**{p['price']}**")
                    st.link_button("👉 前往購買", p['link'])
                    st.markdown("---")
