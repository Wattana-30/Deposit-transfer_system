# ใช้ Python 3.8 เป็นฐาน
FROM python:3.8

# ตั้งค่า directory สำหรับทำงาน
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เข้าไปใน container
COPY requirements.txt /app/

# ติดตั้ง dependencies จาก requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดแอปพลิเคชันเข้าไปใน container
COPY . /app

# ติดตั้งไลบรารี MySQL ที่จำเป็น (เพิ่มให้หากยังไม่มี)
RUN apt-get update && apt-get install -y default-mysql-client

# ตั้งค่าตัวแปรสภาพแวดล้อมสำหรับ Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# ทำให้ Flask เปิดใช้งานเมื่อ container ทำงาน
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
