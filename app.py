import streamlit as st
import gspread
from datetime import datetime
import time

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン (style.cssの読み込み) ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# --- 3. スプレッドシート保存関数 ---
def save_to_sheets(data_list):
    try:
        SPREADSHEET_KEY = '1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI'
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# --- 4. メイン画面の構成 ---
st.title("生産管理入力")

# 日付と曜日
col_d1, col_d2 = st.columns(2)
with col_d1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with col_d2:
    weekday = ["月","火","水","木","金","土","日"][input_date.weekday()]
   # 例：曜日の表示
    st.write("曜日") # ラベルとして表示
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場
area_options = {"盛岡": ["矢巾", "滝沢", "都南", "南"], "花巻": ["桜木", "藤沢", "北上", "江釣子", "水沢", "一関"]}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key="area_select")
with col_a2:
    sel_factory = st.selectbox("工場名", area_options[sel_area], key="factory_select")

st.divider()

# 生産数入力（★ keyだけでOK、valueは書かないのがコツ！）
c1, c2, c3 = st.columns(3)
with c1:
    val_ritai = st.number_input("立体", min_value=0, key="立体")
    val_heimen = st.number_input("平面", min_value=0, key="平面")
with c2:
    val_zubon = st.number_input("ズボン", min_value=0, key="ズボン")
    val_yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with c3:
    val_press = st.number_input("プレス", min_value=0, key="プレス")
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    # 例：5項目合計の表示
    st.write("5項目合計")
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間 (0.25刻み、小数点第2位表示)
col_l, col_r = st.columns(2)
with col_l:
    # step=0.25 にすることで、＋ーボタンで 0.25, 0.50, 0.75... と動きます
    val_work_h = st.number_input(
        "総労働時間 (h)", 
        min_value=0.0, 
        value=0.0, # 初期値を0にします
        step=0.25, 
        format="%.2f", 
        key="work_h"
    )

with col_r:
    # 計算結果も小数点第2位まで表示
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0.00
    st.markdown("人時生産点数")
    # 表示を 0.00 形式に固定するため :.2f を使います
    st.markdown(f'<div class="result-box">{val_prod:.2f}</div>', unsafe_allow_html=True)


st.divider()

# --- 5. 保存・確認ボタンのロジック ---

# 確認フラグの初期化
if 'confirm' not in st.session_state:
    st.session_state.confirm = False

if not st.session_state.confirm:
    if st.button("保存する", use_container_width=True):
        if total_val > 0:
            st.session_state.confirm = True
            st.rerun()
        else:
            st.error("数値を入力してください")
else:
    st.warning("⚠️ この内容でスプレッドシートに保存しますか？")
    conf1, conf2 = st.columns(2)
    
    with conf1:
        if st.button("はい（確定）", use_container_width=True, key="save_final"):
            new_row = [str(input_date), weekday, sel_area, sel_factory, 
                       val_ritai, val_heimen, val_zubon, val_yshirt, 
                       val_press, total_val, val_work_h, val_prod]
            
            if save_to_sheets(new_row):
                st.success("✅ 保存完了！")
                st.balloons()
                
                # 全てのセッション状態を 0 にリセット
                for key in ["立体", "平面", "ズボン", "Yシャツ", "プレス", "work_h"]:
                    st.session_state[key] = 0.0 # 👈 ここも 0.0 に！
                
                st.session_state.confirm = False
                
                time.sleep(1.5)
                st.rerun()

    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()
