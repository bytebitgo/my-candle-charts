#!/bin/bash

# 设置变量
KEYSTORE_PATH="../android/keystore/release.keystore"
KEY_ALIAS="androiddebugkey"
KEYSTORE_PASSWORD="android"
KEY_PASSWORD="android"
VALIDITY=10000

# 创建keystore目录
mkdir -p ../android/keystore

# 生成密钥库
keytool -genkey -v \
  -keystore $KEYSTORE_PATH \
  -alias $KEY_ALIAS \
  -keyalg RSA \
  -keysize 2048 \
  -validity $VALIDITY \
  -storepass $KEYSTORE_PASSWORD \
  -keypass $KEY_PASSWORD \
  -dname "CN=MT5 Candlechart,OU=Development,O=NightTrekSoftware,L=City,S=State,C=CN"

echo "密钥库已生成：$KEYSTORE_PATH"
echo "使用默认密码：android"
echo "使用默认别名：androiddebugkey"

# 生成Base64编码的密钥库
echo "生成Base64编码的密钥库..."
base64 $KEYSTORE_PATH > release.keystore.base64

echo "完成！请将release.keystore.base64的内容添加到GitHub Secrets中的SIGNING_KEY"
echo "同时设置以下GitHub Secrets："
echo "KEY_ALIAS=$KEY_ALIAS"
echo "KEY_STORE_PASSWORD=$KEYSTORE_PASSWORD"
echo "KEY_PASSWORD=$KEY_PASSWORD" 