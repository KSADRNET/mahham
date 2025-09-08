@echo off
echo ========================================
echo   نشر نظام إدارة مهام مركز الموهوبين
echo   على منصة Heroku السحابية
echo   دكتورنت by DrNeT
echo ========================================
echo.

echo التحقق من المتطلبات...

:: التحقق من Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git غير مثبت. حمل من: https://git-scm.com
    pause
    exit /b 1
)
echo ✅ Git مثبت

:: التحقق من Heroku CLI
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Heroku CLI غير مثبت. حمل من: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)
echo ✅ Heroku CLI مثبت

echo.
echo إعداد Git Repository...
if not exist .git (
    git init
    echo ✅ تم إنشاء Git repository
)

git add .
git commit -m "نظام إدارة مهام مركز الموهوبين بحائل"
echo ✅ تم إضافة الملفات

echo.
set /p APP_NAME="أدخل اسم التطبيق (بالإنجليزية، بدون مسافات): "

echo.
echo إنشاء تطبيق Heroku...
heroku create %APP_NAME%
if errorlevel 1 (
    echo ❌ فشل في إنشاء التطبيق. تأكد من أن الاسم غير مستخدم
    pause
    exit /b 1
)

echo.
echo إضافة قاعدة بيانات PostgreSQL...
heroku addons:create heroku-postgresql:mini -a %APP_NAME%

echo.
echo تعيين المتغيرات...
heroku config:set SECRET_KEY="مركز-الموهوبين-بحائل-متعب-المتعب-2025" -a %APP_NAME%

echo.
echo نشر التطبيق...
git push heroku main
if errorlevel 1 (
    echo ❌ فشل في النشر
    pause
    exit /b 1
)

echo.
echo إعداد قاعدة البيانات...
heroku run python -c "from app import create_tables; create_tables()" -a %APP_NAME%

echo.
echo ========================================
echo ✅ تم النشر بنجاح!
echo ========================================
echo.
echo رابط التطبيق: https://%APP_NAME%.herokuapp.com
echo.
echo بيانات المدير:
echo اسم المستخدم: admin
echo كلمة المرور: admin123
echo.
echo شارك الرابط مع زملائك واطلب منهم إنشاء حسابات جديدة
echo.
pause