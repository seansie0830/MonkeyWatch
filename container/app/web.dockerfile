FROM python:3.12

# 設定工作目錄
WORKDIR /app

# 將目前目錄的所有檔案複製到容器的工作目錄
COPY . .

# 安裝 requirements.txt 中列出的套件
RUN pip install -r requirements.txt

# 建立 migrations
#RUN python manage.py makemigrations

# 執行 migrations
#RUN python manage.py migrate

# 暴露端口
EXPOSE 8000

# 執行 Django manage.py
CMD ["python", "manage.py", "runserver"]