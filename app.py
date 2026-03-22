import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- デザイン調整 (上揃え・余白追加) ---
st.markdown("""
    <style>
    /* 全体の文字サイズ統一 */
    html, body, [class*="css"], .stWidgetLabel p, .stMarkdown p {
        font-size: 15px !important;
        margin-bottom: 6px !important; /* ラベル下の余白を少し広げた */
    }
    h1 { font-size: 20px !important; text-align: center; margin-bottom: 20px !important; }

    /* ボックスの高さを42pxで統一 */
    .stNumberInput input, .stSelectbox div, .stDateInput input {
        height: 42px !important;
        font-size: 15px !important;
    }

    /* 黒背景ボックスのデザイン */
    .result-box {
        background-color: #262730; 
        color: #ffffff;
        border: 1px solid rgba(250, 250, 250, 0.2); 
        border-radius: 0.5rem;
        height: 42px !important; 
        min-height: 42px !important;
        display: flex;
        align-items: center; 
        padding: 0px 12px; 
        font-size: 15px !important;
        font-weight: bold;
        box-sizing: border-box;
        width: 100%;
    }
    
    /* 【修正】すべてのカラムを「上基準」で整列 */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: flex-start !important; /* 上揃えに変更 */
    }

    /* ボックス同士の横の間隔を広げる */
    div[data-testid="column"] {
        padding-right: 18px !important; 
    }
    div[data-testid="column"]:last-child {
        padding-right: 0px !important;
    }

    /* 縦方向のブロック間の余白 */
    div[data-testid="stVerticalBlock"] {
        gap: 1.2rem !important; 
    }

    hr { margin: 20px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- スプレッドシート接続 ---
def get_sheet():
    client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

area_data = {"盛岡": ["滝沢", "都南", "矢巾", "南"], "花巻": ["桜木", "藤沢", "北上", "特殊", "江釣子", "水沢", "一関"]}

# --- 保存処理 ---
def save_data():
    t_qty = st.session_state.ritai + st.session_state.heimen + st.session_state.zubon + st.session_state.yshirt + st.session_state.press
    w_h = float(st.session_state.work_h)
    try:
        sheet = get_sheet()
        date_str = st.session_state.input_date.strftime("%Y-%m-%d")
        new_row = [date_str, st.session_state.display_day, st.session_state.area, st.session_state.factory,
                   st.session_state.ritai, st.session_state.heimen, st.session_state.zubon,
                   st.session_state.yshirt, st.session_state.press, t_qty, w_h, round(t_qty/w_h, 2)]
        sheet.append_row(new_row)
        st.success("✅ データを保存しました。")
        # 状態リセット
        st.session_state.ritai = ""
        st.session_state.heimen = ""
        st.session_state.zubon = ""
        st.session_state.yshirt = ""
        st.session_state.press = ""
        st.session_state.work_h = ""
    except Exception as e:
        st.error(f"❌ 保存失敗: {e}")

# --- 画面構成 ---
st.title("生産管理入力")

# 1. 日付と曜日
c_d1, c_d2 = st.columns(2)
with c_d1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with c_d2:
    day_name = ["月","火","水","木","金","土","日"][input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{day_name}</div>', unsafe_allow_html=True)
    st.session_state.display_day = day_name

# 2. 拠点選択
c_a1, c_a2 = st.columns(2)
with c_a1:
    st.selectbox("エリア", list(area_data.keys()), key="area")
with c_a2:
    st.selectbox("工場名", area_data[st.session_state.area], key="factory")

st.divider()

# 3. 生産数
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input("立体", min_value=0, step=1, key="ritai")
    st.number_input("平面", min_value=0, step=1, key="heimen")
with col2:
    st.number_input("ズボン", min_value=0, step=1, key="zubon")
    st.number_input("Yシャツ", min_value=0, step=1, key="yshirt")
with col3:
    st.number_input("プレス", min_value=0, step=1, key="press")
    total_qty = st.session_state.ritai + st.session_state.heimen + st.session_state.zubon + st.session_state.yshirt + st.session_state.press
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_qty}</div>', unsafe_allow_html=True)

st.divider()

# 4. 労働時間と結果
col_l, col_r = st.columns(2)
with col_l:
    # ⏰マークを一旦外し、高さを右側と完全に合わせる
    st.selectbox("総労働時間 (h)", [""3.0","3.15","3.30","3,45","4,0","4.15","4.30","4.45","5.00","5.15","5.30","5.45","6.00","6.15","6.30","6.45","7.00"], key="work_h")
with col_r:
    w_h_val = float(st.session_state.work_h)
    prod = round(total_qty / w_h_val, 2) if w_h_val > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{prod}</div>', unsafe_allow_html=True)

st.divider()

# 5. ボタン
btn1, btn2 = st.columns(2)
with btn1:
    st.button("保存する", use_container_width=True, on_click=save_data, disabled=(total_qty == 0 or float(st.session_state.work_h) == 0))
with btn2:
    if st.button("キャンセル", use_container_width=True):
        st.rerun()
        st.session_state.ritai = ""
        st.session_state.heimen = ""
        st.session_state.zubon = ""
        st.session_state.yshirt = ""
        st.session_state.press = ""
        st.session_state.work_h = ""
        st.rerun()
