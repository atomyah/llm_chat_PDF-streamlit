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

# タイトル
st.set_page_config(page_title="管理画面", page_icon="💻")
st.markdown(
    "<h1 class='jp-san-serif'>PDFアップロードページ（管理者用）</h1>",
    unsafe_allow_html=True,
)
titles()

##################################### タイトルのCSSを良しなに設定 ############################################
# Google FontsからNoto Sans JPフォントをロードする
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

# Robotoフォントをタイトル文字に使用するためのHTMLスタイル
st.markdown(
    """
    <style>
    .jp-san-serif {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 1.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
##################################### タイトルのCSSを良しなに設定～ここまで ############################################


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
##################################### ログイン機能～ここまで ############################################


index = st.session_state.get("index")

prev_uploaded_file = st.session_state.get("prev_uploaded_file", None)

# アプリ開始時に前回のアップロードしたPDFファイル名を読み込む
prev_file_path = "prev_file.txt"
if os.path.exists(prev_file_path):
    with open(prev_file_path, "r") as f:
        prev_file, prev_timestamp = f.read().split("|")
    st.write(f"前回アップロードPDF: {prev_file} (日時: {prev_timestamp})")


# indexをst.session_stateから削除する．
def on_Change_file():
    if "index" in st.session_state:
        st.session_state.pop("index")
    if "prev_uploaded_file" in st.session_state:
        st.session_state.pop("prev_uploaded_file")


upload_file = st.file_uploader(
    label="Q&A対象ファイル",
    type="pdf",
    on_change=on_Change_file,  # ファイルがアップロードされたら（ベクトル化するPDFを新しくアップしたら）on_Change_file()でindexを削除する．
)

# PDFのアップロードとベクトル化
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
