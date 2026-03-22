import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- Googleスプレッドシート接続関数 ---
def get_sheet():
    client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

# --- 拠点データ ---
area_data = {
    "盛岡": ["滝沢", "都南", "矢巾", "南"],
    "花巻": ["桜木", "藤沢", "北上", "特殊", "江釣子", "水沢", "一関"]
}

# --- 【新機能】保存と同時にリセットする関数 ---
def save_and_reset():
    # 入力チェック
    total_qty = st.session_state.ritai + st.session_state.heimen + st.session_state.zubon + st.session_state.yshirt + st.session_state.press
    
    if st.session_state.work_h <= 0:
        st.error("⚠️ 労働時間を入力してください")
        return

    try:
        sheet = get_sheet()
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
        day_of_week = weekday_list[now.weekday()]
        
        # 計算
        productivity = round(total_qty / st.session_state.work_h, 2)
        
        new_row = [
            date_str, day_of_week, st.session_state.area, st.session_state.factory,
            st.session_state.ritai, st.session_state.heimen, st.session_state.zubon,
            st.session_state.yshirt, st.session_state.press,
            total_qty, st.session_state.work_h, productivity
        ]
        
        sheet.append_row(new_row)
        st.toast("✅ スプレッドシートに保存しました！")
        
        # --- ここで数値をリセット（エラーが出ない書き方） ---
        st.session_state.ritai = 0
        st.session_state.heimen = 0
        st.session_state.zubon = 0
        st.session_state.yshirt = 0
        st.session_state.press = 0
        st.session_state.work_h = 0.0
        
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")

# --- メイン画面 ---
st.title("🏭 生産管理入力フォーム")

# 1. エリア・工場名
c1, c2 = st.columns(2)
with c1:
    st.selectbox("エリア", list(area_data.keys()), key="area")
with c2:
    st.selectbox("工場名", area_data[st.session_state.area], key="factory")

st.divider()

# 2. 生産数入力
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input("立体", min_value=0, step=1, key="ritai")
    st.number_input("平面", min_value=0, step=1, key="heimen")
with col2:
    st.number_input("ズボン", min_value=0, step=1, key="zubon")
    st.number_input("Yシャツ", min_value=0, step=1, key="yshirt")
with col3:
    st.number_input("プレス", min_value=0, step=1, key="press")

st.divider()

# 3. 労働時間
st.number_input("⏰ 総労働時間 (h)", min_value=0.0, step=0.1, key="work_h")
st.caption("※10進数で入力（例：1時間30分は 1.5）")

# 4. 保存ボタン（on_clickを使うのがエラー回避のコツ！）
st.button("この内容で保存 💾", use_container_width=True, on_click=save_and_reset)

# 履歴表示
if st.button("📊 最新の5件を表示"):
    try:
        data = get_sheet().get_all_values()
        st.table(data[-5:])
    except:
        st.error("読込失敗")
