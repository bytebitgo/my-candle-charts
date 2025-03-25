FROM nginx:alpine

# 删除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 创建必要的目录
RUN mkdir -p /etc/nginx/ssl
RUN mkdir -p /var/log/nginx

# 设置工作目录
WORKDIR /etc/nginx

# 设置权限
RUN chown -R nginx:nginx /var/log/nginx 