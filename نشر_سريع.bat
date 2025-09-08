@echo off
chcp 65001 >nul
echo ========================================
echo   نشر سريع - نظام إدارة مهام مركز الموهوبين
echo   دكتورنت by DrNeT
echo ========================================
echo.

echo اختر منصة النشر:
echo.
echo 1. Railway (الأسهل والأسرع - مُوصى به)
echo 2. Heroku (تقليدي ومستقر)
echo 3. Render (مجاني بالكامل)
echo 4. إعداد قاعدة بيانات سحابية فقط
echo 5. عرض التعليمات التفصيلية
echo.

set /p choice="اختر رقم (1-5): "

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto heroku
if "%choice%"=="3" goto render
if "%choice%"=="4" goto database
if "%choice%"=="5" goto instructions

echo خيار غير صحيح!
pause
exit /b 1

:railway
echo.
echo ========================================
echo نشر على Railway (الأسهل)
echo ========================================
echo.
echo الخطوات:
echo 1. انتقل إلى: https://railway.app
echo 2. سجل دخول بحساب GitHub
echo 3. ارفع هذا المجلد إلى GitHub أولاً
echo 4. اختر "New Project" في Railway
echo 5. اختر "Deploy from GitHub repo"
echo 6. اختر المستودع
echo 7. أضف PostgreSQL من Services
echo 8. انتظر النشر (5 دقائق)
echo.
echo سيكون الرابط: https://اسم-مشروعك.up.railway.app
echo.
goto end

:heroku
echo.
echo ========================================
echo نشر على Heroku
echo ========================================
echo.
echo تأكد من تثبيت:
echo - Git: https://git-scm.com
echo - Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
echo.
echo ثم شغل: deploy_heroku.bat
echo.
goto end

:render
echo.
echo ========================================
echo نشر على Render
echo ========================================
echo.
echo الخطوات:
echo 1. انتقل إلى: https://render.com
echo 2. سجل دخول بحساب GitHub
echo 3. ارفع المشروع إلى GitHub
echo 4. اختر "New Web Service"
echo 5. اربط المستودع
echo 6. إعدادات البناء:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn app:app
echo 7. أضف PostgreSQL Database منفصل
echo 8. اربط قاعدة البيانات بمتغير DATABASE_URL
echo.
goto end

:database
echo.
echo ========================================
echo إعداد قاعدة بيانات سحابية
echo ========================================
echo.
echo خيارات قواعد البيانات المجانية:
echo.
echo 1. ElephantSQL (PostgreSQL):
echo    - انتقل إلى: https://elephantsql.com
echo    - أنشئ حساب وقاعدة بيانات مجانية
echo    - انسخ URL واستخدمه في DATABASE_URL
echo.
echo 2. Supabase (PostgreSQL مع واجهة):
echo    - انتقل إلى: https://supabase.com
echo    - أنشئ مشروع جديد
echo    - احصل على Connection String
echo.
echo 3. PlanetScale (MySQL):
echo    - انتقل إلى: https://planetscale.com
echo    - أنشئ قاعدة بيانات مجانية
echo.
goto end

:instructions
echo.
echo ========================================
echo التعليمات التفصيلية
echo ========================================
echo.
echo اقرأ الملفات التالية:
echo - دليل_النشر_السحابي.md (تعليمات شاملة)
echo - دليل_الزملاء.md (للمشاركة مع الفريق)
echo.
echo أو شغل:
echo - deploy_railway.bat (للنشر على Railway)
echo - deploy_heroku.bat (للنشر على Heroku)
echo.

:end
echo.
echo ========================================
echo معلومات مهمة بعد النشر:
echo ========================================
echo.
echo بيانات المدير الافتراضي:
echo اسم المستخدم: admin
echo كلمة المرور: admin123
echo.
echo لا تنس:
echo ✅ مشاركة الرابط مع الزملاء
echo ✅ إرسال دليل_الزملاء.md لهم
echo ✅ تغيير كلمة مرور المدير
echo ✅ إنشاء حسابات للمستخدمين
echo.
pause