@echo off
echo ========================================
echo   نشر نظام إدارة مهام مركز الموهوبين
echo   على منصة Railway السحابية
echo   من إبداع الأستاذ: متعب بن مطير المتعب
echo ========================================
echo.

echo الخطوة 1: التحقق من Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git غير مثبت. يرجى تثبيت Git أولاً من: https://git-scm.com
    pause
    exit /b 1
)
echo ✅ Git مثبت

echo.
echo الخطوة 2: إعداد Git Repository...
if not exist .git (
    git init
    echo ✅ تم إنشاء Git repository
) else (
    echo ✅ Git repository موجود
)

echo.
echo الخطوة 3: إضافة الملفات...
git add .
git commit -m "نظام إدارة مهام مركز الموهوبين بحائل - جاهز للنشر"
echo ✅ تم إضافة الملفات

echo.
echo ========================================
echo التعليمات التالية:
echo ========================================
echo.
echo 1. انتقل إلى: https://railway.app
echo 2. سجل دخول بحساب GitHub
echo 3. اختر "New Project"
echo 4. اختر "Deploy from GitHub repo"
echo 5. اختر هذا المستودع
echo 6. أضف PostgreSQL من قائمة Services
echo 7. انتظر النشر (5-10 دقائق)
echo.
echo ========================================
echo بعد النشر:
echo ========================================
echo.
echo • ستحصل على رابط مثل: https://اسم-مشروعك.up.railway.app
echo • شارك الرابط مع زملائك
echo • بيانات المدير: admin / admin123
echo • اطلب من الزملاء إنشاء حسابات جديدة
echo.
echo ========================================

pause