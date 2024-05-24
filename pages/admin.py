## 各モジュールバージョンリスト admin.py
# streamlit@1.25.0
# openai@0.27.8
# langchain@0.0.266
# llama-index@0.8.5
# pypdf@3.15.2
# nltk@3.8.1
# pydantic@1.10.12
import os
from datetime import datetime
import tempfile
import streamlit as st
from pathlib import Path
from llama_index import VectorStoreIndex, ServiceContext
from langchain.chat_models import ChatOpenAI
from llama_index.readers.file.docs_reader import PDFReader
import hmac  # ログイン機能に必要
from japanese_pages import titles
import sqlite3
from itertools import groupby
import csv
import streamlit.components.v1 as components

########### タイトル(japanese_page.pyによりサイドメニューを日本語化) ##############
st.set_page_config(page_title="管理画面", page_icon="💻")
st.write("## 管理画面")
titles()
############ ここまで #############


##################################### ログイン機能 ############################################
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "パスワード", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.
##################################### ログイン機能～ここまで #####################################


############################### チャット履歴データベース接続設定 ##################################
# データベースファイルのパスを設定
root_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(root_dir, "database", "chat_history.db")

# データベースの設定
conn = sqlite3.connect(db_path)
c = conn.cursor()
########################### チャット履歴データベース接続設定～ここまで ############################


########################### PDFファイルアップロード ############################
index = st.session_state.get("index")


# indexをst.session_stateから削除する．
def on_Change_file():
    if "index" in st.session_state:
        st.session_state.pop("index")
    if "prev_uploaded_file" in st.session_state:
        st.session_state.pop("prev_uploaded_file")


st.markdown(f"**🔝Q&A対象PDFファイルをアップロードします**")

# アプリ開始時に前回のアップロードしたPDFファイル名を読み込み画面に表示
prev_uploaded_file = st.session_state.get("prev_uploaded_file", None)
prev_file_path = "prev_file.txt"
if os.path.exists(prev_file_path):
    with open(prev_file_path, "r") as f:
        prev_file, prev_timestamp = f.read().split("|")
    st.write(
        f"前回アップロードPDF: 「{prev_file}」 (アップロード日時: {prev_timestamp})"
    )

upload_file = st.file_uploader(
    label="",
    type="pdf",
    on_change=on_Change_file,  # ファイルがアップロードされたら（ベクトル化するPDFを新しくアップしたら）on_Change_file()でindexを削除する．
)


st.write("---")
########################### PDFファイルアップロード ～ここまで ############################


###################################### PDFのアップロードとベクトル化 #####################################
if upload_file and index is None:
    with st.spinner(text="準備中..."):
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(upload_file.getbuffer())
            prev_uploaded_file = upload_file.name  # アップロードされたファイル名を保存

            documents = PDFReader().load_data(
                file=Path(f.name)
            )  # llama_indexのFileReader(PDFReader)からPDFファイルのテキストを読み込み複数のドキュメントに分割しdocumentsに格納．

            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo", temperature=0
            )  # llama_indexはLanngChainに依存しておりlangchainのChatOpenAIクラスを使ってgpt-3.5-turboを使う準備をする．
            service_context = ServiceContext.from_defaults(
                llm=llm
            )  # ServiceContextはLangChainのllama-indexライブラリで使用されるクラス．from_defaultsメソッドでServiceContextオブジェクトを作成、llm=llmは前に設定したllmオブジェクトをServiceContextに渡している
            # 要はOpenAIのGPT-3.5-turbo言語モデルをLangChain経由で使用する準備をしている．ServiceContextオブジェクトはllama-indexライブラリで使用される様々な機能で必要となる

            index = VectorStoreIndex.from_documents(  # documents(PDFを複数のドキュメントに分割したもの)からベクトル化しindexに格納．
                documents=documents, service_context=service_context
            )

            st.session_state["index"] = index
            st.session_state["prev_uploaded_file"] = (
                prev_uploaded_file  # アップロードされたファイル名をセッションに保存
            )

            # indexの永続化
            index.storage_context.persist("index.json")
            st.success("PDFのベクトル化が完了しました。")

            # 新しいファイルがアップロードされた場合prev_file.txtにPDFファイル名を書き込む
            if prev_uploaded_file:
                current_timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                with open(prev_file_path, "w") as f:
                    f.write(f"{prev_uploaded_file}|{current_timestamp}")

###################################### PDFのアップロードとベクトル化～ここまで #####################################


########################### すべてのチャット履歴の表示（ボタンを押して表示／非表示を切り替える ########################
st.markdown(f"**📝データベースから全てのチャット履歴を表示します**")
# セッションステートを使ってshow_historyを永続化
if (
    "show_history" not in st.session_state
):  # show_historyというブール値のステートを作成.
    st.session_state.show_history = False  # show_historyの初期値はfalse


# ボタンを横並びにするためのコンテナを作成
button_container = st.columns(2)

# ボタンをそれぞれのカラムに配置
with button_container[0]:
    button_style = """
        display: inline-block;
        width: 200px;
    """
    if st.button(
        "チャット履歴を表示", use_container_width=True, key="show_history_button"
    ):
        st.session_state.show_history = True

with button_container[1]:
    button_style = """
        display: inline-block;
        width: 200px;
    """
    if st.button(
        "チャット履歴を非表示", use_container_width=True, key="hide_history_button"
    ):
        st.session_state.show_history = False


# # CSVファイルとして出力するボタン（なぜか無理．あきらめた…）
# output_csv = st.button("チャット履歴をCSVファイルに出力")

# show_historyがtrueならDBから読み込んでチャット履歴を表示する
if st.session_state.show_history:

    c.execute(
        "SELECT session_id, sender, timestamp, message FROM chat_history ORDER BY timestamp ASC"
    )
    chat_history = c.fetchall()

    # session_idごとにグループ化
    grouped_history = groupby(
        chat_history, key=lambda x: x[0]
    )  # from itertools import groupbyによってsession_idごとにグループ化．lambdaは無名関数、xは各タプル（session_id,sender,timestamp,message)、従ってx[0]はsession_id
    # 無名関数は各タプルからsession_idを取り出し、それをグループ化のキーとして使用. つまり、grouped_historyは、チャット履歴のリストをsession_idごとにグループ化したイテレータ.

    # グループごとにチャット履歴を表示
    for session_id, group in grouped_history:
        st.write(f"**セッションID:** {session_id}")
        for session_id, sender, timestamp, message in group:
            if sender == "user":
                st.markdown(f"**ユーザー:** {message}（{timestamp}）")
            else:
                st.markdown(f"**ChatGPT:** {message}（{timestamp}）")
        st.write("---")

    conn.close()
###################################### すべてのチャット履歴の表示～ここまで #####################################


###################################### CSVファイルとして出力する処理 ######################################
# （なぜか無理．あきらめた…）
# if output_csv:
#     c.execute(
#         "SELECT session_id, sender, timestamp, message FROM chat_history ORDER BY timestamp ASC"
#     )
#     chat_history = c.fetchall()

#     # CSVファイルに出力
#     csv_file = "chat_history.csv"
#     with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["session_id", "sender", "timestamp", "message"])
#         writer.writerows(row for row in chat_history)

#     # ファイルをStreamlitで表示
#     with open(csv_file, encoding="utf-8") as f:
#         st.download_button(
#             label="CSVファイルをダウンロード",
#             data=f.read(),
#             file_name="chat_history.csv",
#             mime="text/csv",
#         )
################################## CSVファイルとして出力する処理～ここまで #################################
st.write("---")


################################## データベースからチャットデータを全削除 #################################
st.markdown(f"**🔥【注意】データベースからチャット履歴を全削除します**")

# ボタンのCSSスタイルを定義
danger_button_style = """
<style>
.danger-button {
    background-color: #f44336;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
</style>
"""

# スタイルを適用したボタンを生成
danger_button = f"""
{danger_button_style}
<button class="danger-button" onclick="if (confirm('データベースからチャット履歴をすべて消去します。よろしいですか？')) {{ Streamlit.setComponentValue('delete_history_button', true) }}">
    チャット履歴をデータベースから全削除
</button>
"""

# ボタンをレンダリング
st.markdown(danger_button, unsafe_allow_html=True)


############################# データベースからチャットデータを全削除～ここまで ##############################
