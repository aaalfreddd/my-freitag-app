import streamlit as st
import requests

st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

# 手機優化 CSS
st.markdown("""
    <style>
    .product-box { border: 1px solid #eee; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center; background: white; color: black; }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 1.3rem; margin: 10px 0; }
    img { border-radius: 8px; width: 100%; height: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 直接掃描")
st.caption("直接連線至 Freitag 雲端數據庫 (Algolia)")

def fetch_from_algolia():
    # Freitag 的 Algolia 接口資訊 (這是公開的 API Key)
    api_url = "https://3v8vj997v8-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)%3B%20Browser&x-algolia-api-key=52d194895089311656b69f635581177d&x-algolia-application-id=3V8VJ997V8"
    
    # 搜尋 F306 的參數
    payload = {
        "requests": [
            {
                "indexName": "freitag_prod_en_products",
                "params": "query=F306&hitsPerPage=50&filters=model_id:2211"
            }
        ]
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=15)
        if response.status_code == 200:
            hits = response.json()['results'][0]['hits']
            products = []
            for hit in hits:
                # 只抓取真正有圖片和型號匹配的
                if 'image_url' in hit:
                    products.append({
                        "img": hit['image_url'],
                        "price": f"CHF {hit.get('price', 'N/A')}",
                        "link": "https://www.freitag.ch/en/" + hit.get('url_path', '')
                    })
            return products
        else:
            st.error(f"連線資料庫失敗 (代碼: {response.status_code})")
            return []
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return []

if st.button('🚀 執行深度掃描'):
    with st.spinner('正在同步瑞士資料庫中...'):
        data = fetch_from_algolia()
        if data:
            st.success(f"成功連線！發現 {len(data)} 款 F306 現貨")
            for p in data:
                with st.container():
                    st.markdown(f"""
                    <div class="product-box">
                        <img src="{p['img']}">
                        <div class="price-text">{p['price']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("👉 前往購買", p['link'])
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("資料庫目前回傳 0 筆結果。可能真的賣完了，或是 API Key 有變動。")
