FROM mysql:8.0

# 設定環境變數
ENV MYSQL_ROOT_PASSWORD=mysecretpassword
ENV MYSQL_DATABASE=django_db
ENV MYSQL_USER=django
ENV MYSQL_PASSWORD=your_django_password

# 建立資料夾並設定權限
RUN mkdir -p /var/lib/mysql
RUN chown -R mysql:mysql /var/lib/mysql

# 將資料複製到容器中
# 暴露 MySQL 連接埠
EXPOSE 3306

# 設定健康檢查指令
# 啟動 MySQL 服務
CMD ["mysqld", "--console"] 
# add the console flat to avoid exit 