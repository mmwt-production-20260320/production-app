import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- スマホ向けCSS ---
st.markdown("""
    <style>
    h1 { font-size: 18px !important; text-align: center; }
    html, body, [class*="css"], div[data-testid="stWidgetLabel"] p { font-size: 13px !important; margin-bottom: -15px !important; }
    .stNumberInput input { font-size: 16px !important; }
    hr { margin: 10px 0 !important; }
    .stCaption { font-size: 11px !important; color: #ff4b4b !important; margin-top: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Googleスプレッドシート接続関数 ---
def get_sheet():
    client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

# --- 拠点データ ---
area_data = {
    "盛岡": ["滝沢", "都南", "矢巾", "南"],
    "花巻": ["桜木", "藤沢", "北上", "特殊", "江釣子", "水沢", "一関"]
}

# --- メイン画面 ---
st.title("🏭 生産管理入力フォーム")

# 1. エリア・工場名
c1, c2 = st.columns(2)
with c1:
    selected_area = st.selectbox("エリア", list(area_data.keys()))
with c2:
    available_factories = area_data[selected_area]
    factory_name = st.selectbox("工場名", available_factories)

st.divider()

# 2. 生産数入力
st.subheader("📦 生産数入力")
col1, col2, col3 = st.columns(3)
with col1:
    ritai = st.number_input("立体", min_value=0, step=1, value=0, key="ritai")
    heimen = st.number_input("平面", min_value=0, step=1, value=0, key="heimen")
with col2:
    zubon = st.number_input("ズボン", min_value=0, step=1, value=0, key="zubon")
    yshirt = st.number_input("Yシャツ", min_value=0, step=1, value=0, key="yshirt")
with col3:
    press = st.number_input("プレス", min_value=0, step=1, value=0, key="press")

st.divider()

# 3. 労働時間
work_h = st.number_input("⏰ 総労働時間 (h)", min_value=0.0, step=0.1, value=0.0, key="work_h")
st.caption("※10進数で入力してください（例：1時間30分は 1.5）")

# 4. 自動計算
total_qty = ritai + heimen + zubon + yshirt + press
productivity = round(total_qty / work_h, 2) if work_h > 0 else 0

# 入力チェック
is_empty = (total_qty == 0 or work_h == 0)
if is_empty:
    st.warning("⚠️ 未入力の項目があります。")
else:
    st.info(f"📊 **合計:** {total_qty} 点  /  **生産性:** {productivity}")

# 5. 保存処理
save_button = st.button("この内容で保存 💾", use_container_width=True, disabled=is_empty)

if save_button:
    try:
        with st.spinner("送信中..."):
            sheet = get_sheet()
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
            day_of_week = weekday_list[now.weekday()]
            
            new_row = [
                date_str, day_of_week, selected_area, factory_name,
                ritai, heimen, zubon, yshirt, press,
                total_qty, work_h, productivity
            ]
            
            sheet.append_row(new_row)
            st.success("✅ 保存完了！")
            st.balloons()
            
            # リセット
            for key in ["ritai", "heimen", "zubon", "yshirt", "press", "work_h"]:
                st.session_state[key] = 0 if key != "work_h" else 0.0
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ エラー: {e}")

# 履歴表示
if st.button("📊 最新の5件を表示"):
    try:
        data = get_sheet().get_all_values()
        st.table(data[-5:])
    except:
        st.error("読込失敗")
