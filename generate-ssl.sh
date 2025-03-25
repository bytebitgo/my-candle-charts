#!/bin/bash

# 创建nginx/ssl目录（如果不存在）
mkdir -p nginx/ssl

# 生成私钥和证书
openssl req -x509 \
    -newkey rsa:4096 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -days 365 \
    -nodes \
    -subj "/C=CN/ST=Shanghai/L=Shanghai/O=Development/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# 设置适当的权限
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

echo "SSL证书已生成完成！"
echo "证书位置: nginx/ssl/cert.pem"
 