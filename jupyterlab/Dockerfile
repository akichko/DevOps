FROM python:3

RUN apt-get update \
    && apt-get install -y \
        graphviz \
        iputils-ping \
        iproute2 \
    && pip install --upgrade pip \
    && python -m pip install jupyterlab \
    && python -m pip install numpy \
    && python -m pip install pandas \
    && python -m pip install matplotlib \
    && python -m pip install seaborn \
    && python -m pip install scikit-learn \
    && python -m pip install graphviz \
