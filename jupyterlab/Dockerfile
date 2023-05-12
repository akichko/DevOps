FROM python:3.10

RUN useradd guest -m -s /bin/bash \
    && echo "guest:guestpw" | chpasswd \
    && mkdir -p /run/sshd \
    && apt-get update \
    && apt-get install -y tzdata \
    && apt-get install -y \
        graphviz \
        iputils-ping \
        iproute2 \
        openssh-server \
        mecab \
        libmecab-dev \
        mecab-ipadic-utf8 \
        fonts-ipaexfont-gothic \
    && pip install --upgrade pip \
    && python -m pip install jupyterlab \
        numpy \
        pandas \
        matplotlib \
        japanize-matplotlib \
        seaborn \
        scikit-learn \
        graphviz \
        dtreeviz \
        MeCab \
        gensim \
        statsmodels \
        mojimoji \
        wordcloud \
        tensorflow \
        xgboost \
        transformers \
        sentencepiece \
        torch \
        ipywidgets

