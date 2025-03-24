@echo off
echo 正在创建keystore目录...
mkdir ..\android\keystore 2>nul

echo 正在生成keystore文件...
keytool -genkey -v ^
-keystore ..\android\keystore\release.keystore ^
-alias androiddebugkey ^
-keyalg RSA ^
-keysize 2048 ^
-validity 10000 ^
-storepass android ^
-keypass android ^
-dname "CN=MT5 Candlechart TV,OU=Android,O=Android,L=Mountain View,S=California,C=US"

echo 正在转换为base64...
powershell -Command "$bytes = [System.IO.File]::ReadAllBytes('..\android\keystore\release.keystore'); [System.Convert]::ToBase64String($bytes) | Set-Content -NoNewline ..\android\keystore\keystore-base64.txt"

echo 完成！
echo keystore文件位置: ..\android\keystore\release.keystore
echo base64文件位置: ..\android\keystore\keystore-base64.txt 