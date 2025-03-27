#!/bin/bash

# 启动 Xvfb
Xvfb :99 -screen 0 1024x768x16 &

# 等待 Xvfb 启动
sleep 2

# 启动数据采集器
python collector.py 