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
    /* 数値表示用のおしゃれな枠 */
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
    }
    .metric-label { font-size: 12px; color: #5f6368; }
    .metric-value { font-size: 20px; font-weight: bold; color: #1f77b4; }
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

# --- 保存とリセットの関数 ---
def save_and_reset():
    # セッションから値を取得
    t_qty = st.session_state.ritai + st.session_state.heimen + st.session_state.zubon + st.session_state.yshirt + st.session_state.press
    w_h = float(st.session_state.work_h)
    
    if w_h <= 0:
        st.error("⚠️ 労働時間を選択してください")
        return

    try:
        sheet = get_sheet()
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
        day_of_week = weekday_list[now.weekday()]
        
        prod = round(t_qty / w_h, 2)
        
        new_row = [
            date_str, day_of_week, st.session_state.area, st.session_state.factory,
            st.session_state.ritai, st.session_state.heimen, st.session_state.zubon,
            st.session_state.yshirt, st.session_state.press,
            t_qty, w_h, prod
        ]
        
        sheet.append_row(new_row)
        st.toast("✅ 保存しました！")
        
        # リセット
        st.session_state.ritai = 0
        st.session_state.heimen = 0
        st.session_state.zubon = 0
        st.session_state.yshirt = 0
        st.session_state.press = 0
        st.session_state.work_h = "0.0"
        
    except Exception as e:
        st.error(f"❌ エラー: {e}")

# --- メイン画面 ---
st.title("🏭 生産管理入力フォーム")

# 1. エリア・工場名
c1, c2 = st.columns(2)
with c1:
    st.selectbox("エリア", list(area_data.keys()), key="area")
with c2:
    st.selectbox("工場名", area_data[st.session_state.area], key="factory")

st.divider()

# 2. 生産数入力と合計表示のレイアウト
col1, col2, col3 = st.columns(3)
with col1:
    ritai = st.number_input("立体", min_value=0, step=1, key="ritai")
    heimen = st.number_input("平面", min_value=0, step=1, key="heimen")
with col2:
    zubon = st.number_input("ズボン", min_value=0, step=1, key="zubon")
    yshirt = st.number_input("Yシャツ", min_value=0, step=1, key="yshirt")
with col3:
    press = st.number_input("プレス", min_value=0, step=1, key="press")
    # プレス下・Yシャツ右のスペースに合計を表示
    total_qty = ritai + heimen + zubon + yshirt + press
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">5項目合計</div>
            <div class="metric-value">{total_qty}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 3. 労働時間（プルダウン）と生産点数（横並び）
col_left, col_right = st.columns(2)

with col_left:
    # 労働時間の選択肢（初期値を0にするためリストの先頭に"0.0"を追加）
    work_options = ["0.0", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0", "6.5", "7.0"]
    selected_h = st.selectbox("⏰ 総労働時間 (h)", options=work_options, key="work_h")
    st.caption("※10進数で選択")

with col_right:
    # 人時生産点数の計算と表示
    w_h_val = float(selected_h)
    productivity = round(total_qty / w_h_val, 2) if w_h_val > 0 else 0
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">人時生産点数</div>
            <div class="metric-value">{productivity}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 4. 保存ボタン
# 労働時間が0または合計が0の場合は警告表示
if total_qty == 0 or float(selected_h) == 0:
    st.warning("⚠️ 数値と労働時間を入力してください")
    st.button("この内容で保存 💾", use_container_width=True, disabled=True)
else:
    st.button("この内容で保存 💾", use_container_width=True, on_click=save_and_reset)

# 履歴表示
if st.button("📊 最新の5件を表示"):
    try:
        data = get_sheet().get_all_values()
        st.table(data[-5:])
    except:
        st.error("読込失敗")
