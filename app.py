import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- スマホ向けCSS (見た目の微調整) ---
st.markdown("""
    <style>
    h1 { font-size: 20px !important; text-align: center; margin-bottom: 20px !important; }
    html, body, [class*="css"], div[data-testid="stWidgetLabel"] p { font-size: 13px !important; margin-bottom: -15px !important; }
    .stNumberInput input, .stSelectbox div { font-size: 16px !important; }
    hr { margin: 10px 0 !important; }
    
    /* 計算結果表示用のボックス（薄い緑色・高さ統一） */
    .result-box {
        background-color: #e6ffed; /* 薄い緑 */
        border: 1px solid #dcdfe3;
        border-radius: 4px;
        padding: 8px 12px;
        height: 42px; /* 他の入力欄と高さを揃える */
        font-size: 16px;
        font-weight: bold;
        line-height: 24px;
        color: #1a7f37;
        display: flex;
        align-items: center;
    }
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
        
        st.success("✅ 本日のデータを記録しました。")
        st.balloons()
        clear_inputs()
        
    except Exception as e:
        st.error(f"❌ 保存に失敗しました: {e}")

# --- メイン画面 ---
st.title("生産管理入力") # タイトルを短縮

# 1. エリア・工場名
c1, c2 = st.columns(2)
with c1:
    st.selectbox("エリア", list(area_data.keys()), key="area")
with c2:
    st.selectbox("工場名", area_data[st.session_state.area], key="factory")

st.divider()

# 2. 生産数入力と合計表示
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

# 3. 労働時間と人時生産点数
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

# 4. ボタン配置
btn_save, btn_cancel = st.columns(2)
with btn_save:
    is_invalid = (total_qty == 0 or float(selected_h) == 0)
    st.button("保存する", use_container_width=True, on_click=save_data, disabled=is_invalid)
with btn_cancel:
    st.button("キャンセル", use_container_width=True, on_click=clear_inputs)
