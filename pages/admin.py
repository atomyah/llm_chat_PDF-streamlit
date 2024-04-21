## 各モジュールバージョンリスト admin.py
# streamlit@1.25.0
# openai@0.27.8
# langchain@0.0.266
# llama-index@0.8.5
# pypdf@3.15.2
# nltk@3.8.1
# pydantic@1.10.12
import tempfile
import streamlit as st
from pathlib import Path
from llama_index import VectorStoreIndex, ServiceContext
from langchain.chat_models import ChatOpenAI
from llama_index.readers.file.docs_reader import PDFReader
import hmac  # ログイン機能に必要

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
        font-size: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
##################################### タイトルのCSSを良しなに設定～ここまで ############################################
# タイトル
st.markdown(
    "<h1 class='jp-san-serif'>PDFアップロードページ</h1>",
    unsafe_allow_html=True,
)


##################################### ログイン機能 ############################################
def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("認証情報"):
            st.text_input("ユーザー名", key="username")
            st.text_input("パスワード", type="password", key="password")
            st.form_submit_button("ログイン", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()
##################################### ログイン機能～ここまで ############################################


index = st.session_state.get("index")

prev_uploaded_file = st.session_state.get("prev_uploaded_file", None)


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
        with tempfile.NamedTemporaryFile(delete=False) as f:
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

# 前回アップロードされたファイル名を表示
if prev_uploaded_file:
    st.write(f"前回アップロードされたファイル: {prev_uploaded_file}")
