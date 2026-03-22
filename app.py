import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- スマホ向けCSS (見た目を統一) ---
st.markdown("""
    <style>
    h1 { font-size: 18px !important; text-align: center; }
    html, body, [class*="css"], div[data-testid="stWidgetLabel"] p { font-size: 13px !important; margin-bottom: -15px !important; }
    .stNumberInput input, .stSelectbox div { font-size: 16px !important; }
    hr { margin: 10px 0 !important; }
    /* 合計と点数を入力欄のように見せる設定 */
    .custom-box {
        background-color: #ffffff;
        border: 1px solid #dcdfe3;
        border-radius: 4px;
        padding: 8px;
        height: 38px;
        font-size: 16px;
        line-height: 22px;
        color: #31333f;
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
input_keys = ["ritai", "heimen", "zubon", "yshirt", "press", "work_h"]
for k in input_keys:
    if k not in st.session_state:
        st.session_state[k] = "0.0" if k == "work_h" else 0

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
        
        # 保存完了後のメッセージとリセット
        st.success("✅ 本日のデータを記録しました。")
        st.balloons()
        clear_inputs()
        
    except Exception as e:
        st.error(f"❌ 保存に失敗しました: {e}")

# --- メイン画面 ---
st.title("🏭 生産管理入力フォーム")

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
    st.number_input("プレス", min_value=0, step=1, key="press")
    total_qty = ritai + heimen + zubon + yshirt + st.session_state.press
    st.markdown("5項目合計")
    st.markdown(f'<div class="custom-box">{total_qty}</div>', unsafe_allow_html=True)

st.divider()

# 3. 労働時間と生産点数
col_left, col_right = st.columns(2)
with col_left:
    work_options = ["0.0", "30.0", "30.5", "40.0", "40.5", "50.0", "50.5", "60.0", "60.5", "70.0"]
    selected_h = st.selectbox("⏰ 総労働時間 (h)", options=work_options, key="work_h")
with col_right:
    w_h_val = float(selected_h)
    productivity = round(total_qty / w_h_val, 2) if w_h_val > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="custom-box">{productivity}</div>', unsafe_allow_html=True)

st.divider()

# 4. ボタン配置（横並び）
btn_save, btn_cancel = st.columns(2)

with btn_save:
    # 労働時間が0または合計が0の時は無効化
    is_invalid = (total_qty == 0 or float(selected_h) == 0)
    st.button("保存する", use_container_width=True, on_click=save_data, disabled=is_invalid)

with btn_cancel:
    st.button("キャンセル", use_container_width=True, on_click=clear_inputs)
