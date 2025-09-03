#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار صفحات التطبيق للتأكد من عملها
"""

import requests
import sys

def test_page(url, expected_status=200, description=""):
    """اختبار صفحة واحدة"""
    try:
        response = requests.get(url, timeout=10)
        status = "✅ نجح" if response.status_code == expected_status else f"❌ فشل ({response.status_code})"
        print(f"{status} - {description}: {url}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ خطأ - {description}: {str(e)}")
        return False

def main():
    """اختبار جميع الصفحات"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 اختبار صفحات التطبيق...")
    print("=" * 50)
    
    # الصفحات العامة
    tests = [
        (f"{base_url}/", 200, "الصفحة الرئيسية"),
        (f"{base_url}/login", 200, "صفحة تسجيل الدخول"),
        (f"{base_url}/register", 200, "صفحة التسجيل"),
    ]
    
    # الصفحات المحمية (ستعيد توجيه إلى تسجيل الدخول)
    protected_tests = [
        (f"{base_url}/dashboard", 302, "لوحة التحكم (محمية)"),
        (f"{base_url}/profile", 302, "الملف الشخصي (محمي)"),
        (f"{base_url}/manage_users", 302, "إدارة المستخدمين (محمية)"),
        (f"{base_url}/tasks", 302, "المهام (محمية)"),
        (f"{base_url}/reports", 302, "التقارير (محمية)"),
    ]
    
    success_count = 0
    total_count = 0
    
    # اختبار الصفحات العامة
    print("\n📖 الصفحات العامة:")
    for url, expected, desc in tests:
        if test_page(url, expected, desc):
            success_count += 1
        total_count += 1
    
    # اختبار الصفحات المحمية
    print("\n🔒 الصفحات المحمية (يجب أن تعيد توجيه):")
    for url, expected, desc in protected_tests:
        if test_page(url, expected, desc):
            success_count += 1
        total_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 النتائج: {success_count}/{total_count} اختبار نجح")
    
    if success_count == total_count:
        print("🎉 جميع الاختبارات نجحت! التطبيق يعمل بشكل صحيح.")
        return True
    else:
        print("⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)