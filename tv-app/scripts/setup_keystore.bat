@echo off
echo 创建keystore目录...
mkdir ..\android\keystore 2>nul

echo 生成固定的keystore文件...
keytool -genkey -v ^
-keystore ..\android\keystore\release.keystore ^
-alias androiddebugkey ^
-keyalg RSA ^
-keysize 2048 ^
-validity 10000 ^
-storepass android ^
-keypass android ^
-dname "CN=MT5 Candlechart TV,OU=Android,O=Android,L=Mountain View,S=California,C=US"

echo 完成！
echo keystore文件已生成在: ..\android\keystore\release.keystore 