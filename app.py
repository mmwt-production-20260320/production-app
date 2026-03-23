import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理入力システム", layout="centered")

st.markdown("<h1 style='text-align: center;'>生産管理入力システム</h1>", unsafe_allow_html=True)

# --- スプレッドシート接続設定 ---
# 詳細は Streamlit の Secrets 設定にスプシのURLを登録する必要があります
conn = st.connection("gsheets", type=GSheetsConnection)

# --- セッション状態の初期化（リセット機能用） ---
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 数値入力項目のリスト
items = ["立体", "ズボン", "プレス", "平面", "Yシャツ"]

# 保存ボタンが押された時の処理
def save_data():
    # 本来はここで conn.create() などでスプシに書き込みます
    # 書き込み成功後、入力値をリセットするために session_state を更新
    for item in items:
        st.session_state[item] = 0
    st.success("データを保存しました！")

# --- 入力フォーム ---
# vertical_alignment="end" で横の入力欄の高さを揃えます
col1, col2 = st.columns(2, vertical_alignment="end")

with col1:
    input_date = st.date_input("入力日", value=datetime.now())
    area = st.selectbox("エリア", ["成田", "千葉", "東京"]) # 例

with col2:
    # 曜日は日付から自動算出も可能ですが、一旦テキスト表示
    weekday = st.text_input("曜日", value=input_date.strftime("%a")) 
    factory = st.selectbox("工場名", ["成田第一", "成田第二"]) # 例

st.divider()

# 数値入力エリア（2列または3列構成）
c1, c2, c3 = st.columns(3, vertical_alignment="end")
with c1:
    v_rittai = st.number_input("立体", min_value=0, key="立体")
    v_heimen = st.number_input("平面", min_value=0, key="平面")
with c2:
    v_zubon = st.number_input("ズボン", min_value=0, key="ズボン")
    v_yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with c3:
    v_press = st.number_input("プレス", min_value=0, key="プレス")
    total = v_rittai + v_zubon + v_press + v_heimen + v_yshirt
    st.number_input("5項目合計", value=total, disabled=True)

st.divider()

col_work, col_prod = st.columns(2, vertical_alignment="end")
with col_work:
    work_hours = st.selectbox("総労働時間 (h)", [i for i in range(1, 25)])
with col_prod:
    # 人時生産点数の計算例（合計 / 労働時間）
    prod_score = total / work_hours if work_hours > 0 else 0
    st.number_input("人時生産点数", value=float(prod_score), disabled=True)

# --- ボタンエリア ---
st.write("") # スペース
btn_save, btn_cancel = st.columns(2)

with btn_save:
    if st.button("保存する", type="primary", use_container_width=True):
        # ここでスプシへのデータ転送を実行
        # 例: data = pd.DataFrame([[input_date, ...]])
        # conn.create(data=data)
        save_data()

with btn_cancel:
    if st.button("キャンセル", use_container_width=True):
        st.warning("入力をキャンセルしました")
