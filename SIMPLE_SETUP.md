# 🚀 Simple Setup - No Docker Required!

## للإعداد السريع بدون دوكر

### 📋 المتطلبات (Requirements)

**Windows:**
- GCC compiler (MinGW)
- Python 3.7+

**Linux/Mac:**
- GCC
- Python 3.7+

---

## 🎯 طريقة التشغيل (3 خطوات فقط)

### الخطوة 1: البناء (Build)
```bash
# Windows
build.bat

# Linux/Mac
chmod +x build.sh
./build.sh
```

### الخطوة 2: التشغيل (Start)
```bash
# Windows
start.bat

# Linux/Mac  
chmod +x start.sh
./start.sh
```

### الخطوة 3: فتح المتصفح (Open Browser)
اذهب إلى: **http://localhost:8000**

---

## 📱 ما ستراه (What You'll See)

- **رسوم بيانية مباشرة** لـ 10 أصول رقمية
- **إشارات تداول** (شراء/بيع)
- **إحصائيات التداول** (الرصيد، الربح، الصفقات)
- **توقيت دقيق** بالميكروثانية
- **خوارزمية EDF** للجدولة

---

## 🔧 إذا لم يعمل (Troubleshooting)

### مشكلة في بناء الـ C bot:
```bash
# Windows
# تأكد من تثبيت MinGW
# أو استخدم: gcc -o market_bot.exe market_bot.c -lpthread

# Linux/Mac
gcc -o market_bot market_bot.c -lpthread
```

### مشكلة في بايثون:
```bash
# تثبيت المكتبات المطلوبة
pip install fastapi uvicorn websockets

# تحقق من إصدار بايثون
python --version
```

### المنافذ مشغولة (Ports in use):
```bash
# Windows
netstat -ano | findstr :8080
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8080
lsof -i :8000
```

---

## 🛑 كيفية الإيقاف (How to Stop)

```bash
# Windows
# أغلق نوافذ CMD التي فتحت

# Linux/Mac
# اضغط Ctrl+C في كل نافذة
```

---

## 📊 معلومات النظام (System Info)

- **الواجهة الرئيسية**: http://localhost:8000
- **حالة الخادم**: http://localhost:8000/health
- **المراكز المفتوحة**: http://localhost:8000/positions

---

## 🎮 مشاركة مع الأصدقاء (Share with Friends)

### أرسل لهم هذا:
```
🚀 نظام تداول الأصول الرقمية

1. حمّل المشروع
2. شغّل: build.bat (Windows) أو ./build.sh (Linux/Mac)
3. شغّل: start.bat (Windows) أو ./start.sh (Linux/Mac)
4. افتح: http://localhost:8000

مبروك! نظام التداول جاهز! 🎉
```

---

## 🆞 المساعدة (Help)

### تحقق من:
1. **Python يعمل**: `python --version`
2. **GCC يعمل**: `gcc --version`
3. **المنافذ حرة**: 8080 و 8000

### إذا استمرت المشكلة:
1. أرسل رسالة الخطأ
2. تحقق من تثبيت كل المتطلبات
3. جرب التشغيل يدوياً

---

## 📞 الاتصال (Contact)

إذا واجهت أي مشاكل، لا تتردد في طلب المساعدة!

**مبروك! 🎉 نظام التداول يعمل الآن!**
