import streamlit as st
import gspread
from datetime import datetime
import time  # 👈 これを一番上に追加してください！

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン (外部の style.css を読み込む) ---
# 先ほど作った style.css をここで合体させます
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# --- 4. リセット関数（中身をスッキリさせました） ---
def reset_all_fields():
    # 【重要】入力欄の「key」と完全に同じ名前を指定します
                for key in ["立体", "平面", "ズボン", "Yシャツ", "プレス", "work_h"]:
                    if key in st.session_state:
                        st.session_state[key] = 0 # 削除ではなく0を直接代入
                st.session_state.confirm = False

# --- 5. メイン画面の構成 ---
st.title("生産管理入力")

# 日付と曜日
col_d1, col_d2 = st.columns(2)
with col_d1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with col_d2:
    weekday = ["月","火","水","木","金","土","日"][input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場
area_options = {"盛岡": ["滝沢", "都南", "南", "矢巾"], "花巻": ["桜木", "藤沢", "北上", "江釣子", "水沢", "一関"]}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key="area_select")
with col_a2:
    sel_factory = st.selectbox("工場名", area_options[sel_area], key="factory_select")

st.divider()

# 生産数入力
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
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間
col_l, col_r = st.columns(2)
with col_l:
    val_work_h = st.selectbox("総労働時間 (h)", [round(x*0.5, 1) for x in range(1, 21)], key="work_h")
with col_r:
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{val_prod}</div>', unsafe_allow_html=True)

st.divider()

st.divider()

# --- 6. 保存・確認ボタンのロジック ---

# セッション状態の初期化
if "confirm" not in st.session_state:
    st.session_state.confirm = False

# まだ「保存ボタン」を押していない時
if not st.session_state.confirm:
    if st.button("保存する", use_container_width=True):
        if total_val > 0:
            st.session_state.confirm = True
            st.rerun()
        else:
            st.error("数値を入力してください")

# 「保存ボタン」が押されて、確認モードになっている時
else:
    st.warning("⚠️ この内容でスプレッドシートに保存しますか？")
    conf1, conf2 = st.columns(2)
    
    with conf1:
        # 【重要】ボタン自体にリセット機能を持たせることはできないので
        # 保存成功後にページを「完全リフレッシュ」する方法に切り替えます
        if st.button("はい（確定）", use_container_width=True, key="save_final"):
            new_row = [str(input_date), weekday, sel_area, sel_factory, 
                       val_ritai, val_heimen, val_zubon, val_yshirt, 
                       val_press, total_val, val_work_h, val_prod]
            
            if save_to_sheets(new_row):
                st.success("✅ 保存完了！")
                st.balloons()
                
                # --- 強力リセット開始 ---
                # 1. すべての入力キーをリスト化
                reset_keys = ["立体", "ズボン", "プレス", "平面", "Yシャツ", "work_h", "confirm"]
                
                # 2. セッションから完全に削除（これで「記憶」を消します）
                for key in reset_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # 3. 重要：待ち時間を入れずに「即」rerunする
                # time.sleep(1) を入れると、消す前の値が画面に残ってしまうことがあります
                st.rerun()
