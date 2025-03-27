FROM python:3.8-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY collector.py .
COPY config.ini .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 MT5
RUN wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
RUN mkdir -p /root/.wine/drive_c/Program\ Files/MetaTrader\ 5

# 创建日志目录
RUN mkdir -p logs

# 设置环境变量
ENV DISPLAY=:99
ENV MT5_PATH="/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"

# 启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"] 