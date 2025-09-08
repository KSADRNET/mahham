#!/usr/bin/env python3
"""
اختبار نظام التحديث التلقائي
Test Auto Update System
دكتورنت by DrNeT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_updater import AutoUpdater
import json

def test_updater():
    """اختبار جميع وظائف نظام التحديث"""
    
    print("🚀 اختبار نظام التحديث التلقائي")
    print("=" * 50)
    
    # إنشاء مثيل من المحدث
    updater = AutoUpdater()
    
    # 1. اختبار الاتصال بـ GitHub
    print("\n1️⃣ اختبار الاتصال بـ GitHub...")
    github_info = updater.get_github_latest_commit()
    if github_info:
        print("✅ نجح الاتصال بـ GitHub")
        print(f"   آخر commit: {github_info['sha']}")
        print(f"   الرسالة: {github_info['message']}")
        print(f"   المؤلف: {github_info['author']}")
    else:
        print("❌ فشل الاتصال بـ GitHub")
    
    # 2. اختبار فحص التحديثات
    print("\n2️⃣ اختبار فحص التحديثات...")
    update_check = updater.check_for_updates()
    print(f"   الحالة: {update_check['status']}")
    print(f"   الرسالة: {update_check['message']}")
    
    # 3. اختبار حالة Railway
    print("\n3️⃣ اختبار حالة Railway...")
    railway_status = updater.check_railway_status()
    print(f"   الحالة: {railway_status['status']}")
    print(f"   الرسالة: {railway_status['message']}")
    if 'response_time' in railway_status:
        print(f"   زمن الاستجابة: {railway_status['response_time']:.2f} ثانية")
    
    # 4. اختبار النسخة الاحتياطية
    print("\n4️⃣ اختبار النسخة الاحتياطية...")
    backup_result = updater.create_backup()
    print(f"   الحالة: {backup_result['status']}")
    print(f"   الرسالة: {backup_result['message']}")
    if 'backup_file' in backup_result:
        print(f"   ملف النسخة: {backup_result['backup_file']}")
    
    # 5. اختبار حالة النظام الشاملة
    print("\n5️⃣ اختبار حالة النظام الشاملة...")
    system_status = updater.get_system_status()
    
    if 'github' in system_status and system_status['github']:
        print("   ✅ GitHub: متصل")
    else:
        print("   ❌ GitHub: غير متصل")
    
    if 'railway_status' in system_status:
        if system_status['railway_status']['status'] == 'online':
            print("   ✅ Railway: يعمل")
        else:
            print("   ❌ Railway: مشكلة")
    
    if 'update_status' in system_status:
        status = system_status['update_status']['status']
        if status == 'up_to_date':
            print("   ✅ التحديث: محدث")
        elif status == 'update_available':
            print("   ⚠️ التحديث: متاح")
        else:
            print(f"   ❓ التحديث: {status}")
    
    print("\n" + "=" * 50)
    print("🎉 انتهى الاختبار!")
    
    return system_status

def save_test_results(results):
    """حفظ نتائج الاختبار"""
    try:
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("💾 تم حفظ نتائج الاختبار في test_results.json")
    except Exception as e:
        print(f"❌ فشل في حفظ النتائج: {e}")

if __name__ == "__main__":
    try:
        results = test_updater()
        save_test_results(results)
        
        print("\n📋 ملخص النتائج:")
        print("   - إذا كانت جميع الاختبارات ناجحة، النظام جاهز للاستخدام")
        print("   - إذا فشل اختبار GitHub، تحقق من الاتصال بالإنترنت")
        print("   - إذا فشل اختبار Railway، تحقق من حالة التطبيق")
        print("   - ملف النتائج محفوظ في test_results.json")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الاختبار: {e}")
        sys.exit(1)