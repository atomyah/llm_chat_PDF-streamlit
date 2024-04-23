## 各モジュールバージョンリスト chat.py
# streamlit@1.25.0
# openai@0.27.8
# langchain@0.0.266
# llama-index@0.8.5
# pypdf@3.15.2
# nltk@3.8.1
# pydantic@1.10.12
import os
import tempfile
import shutil
import json
import streamlit as st
from langchain.chat_models import ChatOpenAI

# from llama_index import VectorStoreIndex, StorageContext, ServiceContext
from llama_index import (
    LLMPredictor,
    #    PromptTemplate,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.indices.base import BaseIndex
import hmac  # ログイン機能に必要
from japanese_pages import titles


# タイトル
st.set_page_config(page_title="チャット", page_icon="💬")
st.markdown(
    "<h1 class='jp-san-serif'>チャットページ</h1>",
    unsafe_allow_html=True,
)
titles()

st.write(
    '<span style="color:blue;">○○○○（例：社内規則）について何でも聞いてください...😉</span>',
    unsafe_allow_html=True,
)


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
        font-size: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
##################################### タイトルのCSSを良しなに設定～ここまで ############################################


############# admin.pyでベクトル化されたindex.json配下を読み込む機能 ##################
if "index" not in st.session_state:
    with tempfile.TemporaryDirectory() as temp_dir:
        # index.jsonがあるディレクトリのパス
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_dir = os.path.join(app_root, "index.json")

        # st.write("index_dir...", index_dir)
        index_files = [
            os.path.join(index_dir, "docstore.json"),
            os.path.join(index_dir, "index_store.json"),
            os.path.join(index_dir, "vector_store.json"),
        ]

        # インデックスファイルをテンポラリディレクトリにコピー
        for file in index_files:
            shutil.copy(file, temp_dir)

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", temperature=0
        )  # llama_indexはLanngChainに依存しておりlangchainのChatOpenAIクラスを使ってgpt-3.5-turboを使う準備をする．
        # service_context = ServiceContext.from_defaults(llm=llm)
        service_context = ServiceContext.from_defaults(
            llm_predictor=LLMPredictor(
                llm=ChatOpenAI(
                    temperature=0, model_name="gpt-3.5-turbo-0613", max_tokens=512
                )
            )
        )
        storage_context = StorageContext.from_defaults(persist_dir=temp_dir)
        # index = VectorStoreIndex.load_from_disk(
        #     temp_dir, service_context=service_context
        # )
        # インデックスファイルの読み込み
        with open(os.path.join(temp_dir, "index_store.json"), "rb") as f:
            index_bytes = f.read()
        # index = VectorStoreIndex.load_from_bytes(
        #     index_bytes, service_context=service_context
        # )
        index = load_index_from_storage(
            storage_context=storage_context, service_context=service_context
        )

        st.session_state["index"] = index

index = st.session_state["index"]
############# admin.pyでベクトル化されたindex.json配下を読み込む機能～ここまで ##################

# チャット履歴の初期化
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# テキスト入力フォームの領域
# user_input = st.text_input(
#     "質問を入力してください", key="input", placeholder="ここに入力..."
# )
user_input = st.chat_input(
    "...質問を入力ください"
)  # st.text_inputだと上記のようにlabelなど色々設定できる代わりに中央に表示されてしまう．
if user_input:
    with st.spinner("考え中..."):
        query_engine = index.as_query_engine()
        query = "\n".join(
            [f"Human: {msg}" for msg in st.session_state["chat_history"][-10:]]
            + [f"Human: {user_input}"]
        )
        answer = query_engine.query(query)
        st.session_state["chat_history"].append(user_input)
        st.session_state["chat_history"].append(answer.response)

# 対話履歴の表示
# session_state["chat_history"]の配列の奇数番目のものならユーザーの質問、偶数番目ならChatGPTの回答、として表示
for i, message in enumerate(st.session_state["chat_history"]):
    if i % 2 == 0:
        st.markdown(f"**あなた:** {message}")
    else:
        st.markdown(f"**ChatGPT:** {message}")
