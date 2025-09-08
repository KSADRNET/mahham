#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إدارة مهام مركز الموهوبين بحائل
دكتورنت by DrNeT
"""

import requests
import time
import sys

def test_system():
    """اختبار النظام للتأكد من عمله بشكل صحيح"""
    
    print("=" * 50)
    print("اختبار نظام إدارة مهام مركز الموهوبين بحائل")
    print("دكتورنت by DrNeT")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # اختبار الاتصال بالخادم
    print("\n1. اختبار الاتصال بالخادم...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ الخادم يعمل بشكل صحيح")
        else:
            print(f"❌ خطأ في الخادم: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بالخادم")
        print("تأكد من تشغيل النظام أولاً باستخدام: python app.py")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False
    
    # اختبار صفحة تسجيل الدخول
    print("\n2. اختبار صفحة تسجيل الدخول...")
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ صفحة تسجيل الدخول تعمل")
        else:
            print(f"❌ خطأ في صفحة تسجيل الدخول: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في اختبار تسجيل الدخول: {e}")
    
    # اختبار صفحة التسجيل
    print("\n3. اختبار صفحة التسجيل...")
    try:
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ صفحة التسجيل تعمل")
        else:
            print(f"❌ خطأ في صفحة التسجيل: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في اختبار التسجيل: {e}")
    
    print("\n" + "=" * 50)
    print("تم الانتهاء من الاختبار")
    print("=" * 50)
    
    print("\n📋 معلومات مهمة:")
    print("• رابط النظام: http://localhost:5000")
    print("• اسم المستخدم الافتراضي: admin")
    print("• كلمة المرور الافتراضية: admin123")
    
    return True

if __name__ == "__main__":
    test_system()
    input("\nاضغط Enter للخروج...")