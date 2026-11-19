FROM python:3.11-slim

WORKDIR /app

# نصب ابزارهای سیستمی لازم و پاکسازی کش برای کاهش حجم ایمیج
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کدهای هسته بک‌اند و دارایی‌های رابط کاربری
COPY ./app /app/app
COPY ./public /app/public

# ایجاد کاربر غیرریشه برای ارتقای امنیت کانتینر
RUN useradd -m -u 1000 aurora && chown -R aurora:aurora /app
USER aurora

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
