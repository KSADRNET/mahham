@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 🚀 نشر نظام التحديث التلقائي
echo ========================================
echo.

echo 📋 التحقق من الملفات الجديدة...
if not exist "auto_updater.py" (
    echo ❌ ملف auto_updater.py غير موجود
    pause
    exit /b 1
)

if not exist "templates\system_update.html" (
    echo ❌ ملف system_update.html غير موجود
    pause
    exit /b 1
)

echo ✅ جميع الملفات موجودة

echo.
echo 🔧 اختبار النظام محلياً...
python test_update_system.py
if errorlevel 1 (
    echo ❌ فشل في اختبار النظام
    pause
    exit /b 1
)

echo.
echo 📤 رفع التحديثات إلى GitHub...
git add .
git commit -m "إضافة نظام التحديث التلقائي - Auto Update System"
git push origin main

if errorlevel 1 (
    echo ❌ فشل في رفع التحديثات
    pause
    exit /b 1
)

echo ✅ تم رفع التحديثات بنجاح

echo.
echo 🚂 انتظار تحديث Railway...
echo يرجى الانتظار 2-3 دقائق لتحديث Railway تلقائياً
echo أو يمكنك الذهاب لـ Railway Dashboard وإجبار إعادة النشر

echo.
echo 🎉 تم نشر نظام التحديث التلقائي بنجاح!
echo.
echo 📋 الخطوات التالية:
echo 1. انتظر تحديث Railway (2-3 دقائق)
echo 2. اذهب للتطبيق وسجل دخول كمدير
echo 3. انقر على "تحديث النظام" في الشريط الجانبي
echo 4. اختبر جميع الميزات الجديدة
echo.
echo 🌐 رابط التطبيق: https://web-production-c090b.up.railway.app
echo.
pause