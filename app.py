import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- スマホ向けCSS (デザインの完全統一) ---
st.markdown("""
    <style>
    h1 { font-size: 20px !important; text-align: center; margin-bottom: 10px !important; }
    html, body, [class*="css"], div[data-testid="stWidgetLabel"] p { font-size: 13px !important; margin-bottom: -15px !important; }
    
    /* 入力欄と表示ボックスの共通スタイル */
    .stNumberInput input, .stSelectbox div, .stDateInput input {
        font-size: 16px !important;
        height: 45px !important; /* 標準ボックスの高さを固定 */
    }

    /* 計算結果ボックスを標準の入力欄に完全に合わせる */
    .result-box {
        background-color: #262730; 
        color: #ffffff;
        border: 1px solid rgba(250, 250, 250, 0.2); 
        border-radius: 0.5rem;
        padding: 0px 12px;
        /* 標準のnumber_input等と高さを揃えるための設定 */
        height: 45px !important; 
        min-height: 45px !important;
        margin-top: 1px; /* 微調整 */
        font-size: 16px;
        font-weight: bold;
        display: flex;
        align-items: center;
        box-sizing: border-box;
        width: 100%;
    }
    hr { margin: 10px 0 !important; }
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

# --- 初期状態のセットアップ ---
if "work_h" not in st.session_state:
    st.session_state.work_h = "0.0"

# --- 関数：リセット処理 ---
def clear_inputs():
    st.session_state.ritai = 0
    st.session_state.heimen = 0
    st.session_state.zubon = 0
    st.session_state.yshirt = 0
    st.session_state.press = 0
    st.session_state.work_h = "0.0"

# --- 関数：保存処理 ---
def save_data():
    t_qty = st.session_state.ritai + st.session_state.heimen + st.session_state.zubon + st.session_state.yshirt + st.session_state.press
    w_h = float(st.session_state.work_h)
    
    try:
        sheet = get_sheet()
        date_str = st.session_state.input_date.strftime("%Y-%m-%d")
        day_of_week = st.session_state.display_day
        
        prod = round(t_qty / w_h, 2)
        
        new_row = [
            date_str, day_of_week, st.session_state.area, st.session_state.factory,
            st.session_state.ritai, st.session_state.heimen, st.session_state.zubon,
            st.session_state.yshirt, st.session_state.press,
            t_qty, w_h, prod
        ]
        sheet.append_row(new_row)
        
        st.success("✅ 本日のデータを記録しました。")
        st.balloons()
        clear_inputs()
        
    except Exception as e:
        st.error(f"❌ 保存に失敗しました: {e}")

# --- メイン画面 ---
st.title("生産管理入力")

# 1. 日付と曜日
d_col1, d_col2 = st.columns(2)
with d_col1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with d_col2:
    weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
    day_name = weekday_list[input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{day_name}</div>', unsafe_allow_html=True)
    st.session_state.display_day = day_name

# 2. エリア・工場名
c1, c2 = st.columns(2)
with c1:
    st.selectbox("エリア", list(area_data.keys()), key="area")
with c2:
    st.selectbox("工場名", area_data[st.session_state.area], key="factory")

st.divider()

# 3. 生産数入力と合計表示
col1, col2, col3 = st.columns(3)
with col1:
    ritai = st.number_input("立体", min_value=0, step=1, key="ritai")
    heimen = st.number_input("平面", min_value=0, step=1, key="heimen")
with col2:
    zubon = st.number_input("ズボン", min_value=0, step=1, key="zubon")
    yshirt = st.number_input("Yシャツ", min_value=0, step=1, key="yshirt")
with col3:
    press = st.number_input("プレス", min_value=0, step=1, key="press")
    total_qty = ritai + heimen + zubon + yshirt + press
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_qty}</div>', unsafe_allow_html=True)

st.divider()

# 4. 労働時間と人時生産点数
col_left, col_right = st.columns(2)
with col_left:
    work_options = ["0.0", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0", "6.5", "7.0"]
    selected_h = st.selectbox("⏰ 総労働時間 (h)", options=work_options, key="work_h")
with col_right:
    w_h_val = float(selected_h)
    productivity = round(total_qty / w_h_val, 2) if w_h_val > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{productivity}</div>', unsafe_allow_html=True)

st.divider()

# 5. ボタン配置
btn_save, btn_cancel = st.columns(2)
with btn_save:
    is_invalid = (total_qty == 0 or float(selected_h) == 0)
    st.button("保存する", use_container_width=True, on_click=save_data, disabled=is_invalid)
with btn_cancel:
    st.button("キャンセル", use_container_width=True, on_click=clear_inputs)
