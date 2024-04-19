FROM python:3.11.4

RUN apt-get update &&\
    apt-get -y install locales &&\
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN pip install --upgrade pip

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python - --version 1.5.1

# Poetryのパスの設定．/home/atom/.local/bin:$PATH"の場合も｡
# 参考：https://qiita.com/siruku6/items/90a34539b954de717de6
ENV PATH /root/.local/bin:$PATH

# Poetryが仮想環境を生成しないようにする. 一応②の設定(docker-compose.ymlに記述)があるためコメントアウトしておく
#RUN poetry config virtualenvs.create false

