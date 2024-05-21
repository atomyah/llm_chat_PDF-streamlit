## llm chat from PDF documents informationo


 ### コンテナに入り込むコマンド
 普通にコンテナに入るコマンド: docker exec -it llm-streamlit bash  
 sudo権限で入るには: docker exec -it -u 0 llm-streamlit bash  
 WSLのUbuntuにおいて、/appの絶対パスは/mnt/<ドライブレター>/appのようになる  
 例：/mnt/c/app  

 ### コンテナが出来た後
 ① poetry init コマンドで初期化(poetryはDockerファイルのRUNでインストール)．聞かれる問いにはすべてエンター．pyproject.tomlファイルができる．そのファイルの`packages=`の行は削除．さらにpyproject.tomlと同じ階層にREADME.mdを作成．  
 ② poetry config virtualenvs.in-project true --local コマンドを打って、poetry.tomlファイルを同じ階層に作成する．これはこのプロジェクトで使うpythonパッケージがこのディレクトリ以下に置かれる、という設定．poetry run python --versionでバージョンが3.11.4と確認できればOK.  
 ③ poetry add streamlit@1.25.0 コマンドでStreamlitをインストール．  
 ④ 開発サーバー起動：poetry run streamlit run home.py  
 ⑤ Black Formatter拡張機能をインストール→参考：https://maku.blog/p/4oybku6/  
 ⑥ poetry add openai@0.27.8   
 ⑦ Udemyのように、.streamlitフォルダを作成しその中にsecrets.tomlファイルを作成し、OPENAI_API_KEY = "sk-aMQhj71GZ4xxxxxxxxxxxxxxxxxxxx" を記述。dotenvで.envファイルに記述、のやり方だとqa.pyはエラーになる．  
 ⑧ langchainをインストール．poetry add langchain@0.0.266  
 ⑨ llama-index類をインストール．poetry add llama-index@0.8.5 pypdf@3.15.2 nltk@3.8.1  
 ⑩ JSONスキーマ生成ツールpydanticが上記のインストールにより1.10.15が入る．これだとエラーとなるのでpoetry add pydantic@1.10.12でpydanticをダウングレードする．  
 ⑪ ここからはオプション機能：sqliteをインストールしてチャット履歴をDBに記録する.まず、sudo apt update、suto apt install -y sqlite3、でsqlite3をインストール  
 コマンド：sudo sqlite3 chat_history.db（sudoでアクセスしないとdelete from テーブルやdrop テーブルができない。  
