@echo off
echo ========================================
echo   إعداد نظام إدارة مهام مركز الموهوبين
echo   صنع بواسطة دكتورنت للنظم الأمنية - By DrNeT 0165395559
echo ========================================
echo.
echo جاري تثبيت المتطلبات...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo تم الانتهاء من الإعداد بنجاح!
echo ========================================
echo.
echo يمكنك الآن تشغيل النظام باستخدام:
echo start.bat
echo.
pause