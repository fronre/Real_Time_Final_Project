FROM gcc:latest

WORKDIR /app
# تثبيت الأدوات المساعدة (مفيد جداً للتنقيح Debugging)
RUN apt-get update && apt-get install -y \
    make \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# نسخ جميع ملفات المشروع (الكود والميك فايل)
COPY . .

# خيار 1: إذا كان الـ Makefile جاهزاً، استخدمه:
# RUN make

# خيار 2: التجميع اليدوي (تأكد من ترتيب المكتبات)
RUN gcc -Wall -Wextra -std=c99 -o market_bot market_bot.c -lpthread

# فتح المنفذ المطلوبة
EXPOSE 8080

# تشغيل البوت
CMD ["./market_bot"]