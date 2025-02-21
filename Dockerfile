# 使用 Python 3.9
FROM python:3.9

# 設定工作目錄
WORKDIR /app

# 複製需求安裝檔
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 暴露 5000 埠
EXPOSE 5000

# 啟動 Flask 服務
CMD ["python", "app.py"]
