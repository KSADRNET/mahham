#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخ احتياطي لملفات الإنجاز
مركز الموهوبين بحائل
"""

import os
import shutil
import sqlite3
from datetime import datetime
import zipfile

def backup_achievements():
    """إنشاء نسخة احتياطية من ملفات الإنجاز"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_achievements_{timestamp}"
    
    print(f"🔄 بدء إنشاء النسخة الاحتياطية...")
    print(f"📁 مجلد النسخة الاحتياطية: {backup_dir}")
    
    try:
        # إنشاء مجلد النسخة الاحتياطية
        os.makedirs(backup_dir, exist_ok=True)
        
        # نسخ قاعدة البيانات
        if os.path.exists('tasks.db'):
            shutil.copy2('tasks.db', os.path.join(backup_dir, 'tasks.db'))
            print("✅ تم نسخ قاعدة البيانات")
        
        # نسخ مجلد الملفات المرفوعة
        if os.path.exists('uploads'):
            shutil.copytree('uploads', os.path.join(backup_dir, 'uploads'))
            print("✅ تم نسخ مجلد الملفات المرفوعة")
        
        # إنشاء ملف معلومات النسخة الاحتياطية
        info_file = os.path.join(backup_dir, 'backup_info.txt')
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"نسخة احتياطية لملفات الإنجاز\n")
            f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"النظام: مركز الموهوبين بحائل\n")
            f.write(f"المطور: دكتورنت by DrNeT\n\n")
            
            # إحصائيات قاعدة البيانات
            if os.path.exists('tasks.db'):
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM achievement")
                    achievements_count = cursor.fetchone()[0]
                    f.write(f"عدد الإنجازات: {achievements_count}\n")
                    
                    cursor.execute("SELECT COUNT(*) FROM achievement_file")
                    files_count = cursor.fetchone()[0]
                    f.write(f"عدد الملفات: {files_count}\n")
                    
                    cursor.execute("SELECT COUNT(*) FROM user")
                    users_count = cursor.fetchone()[0]
                    f.write(f"عدد المستخدمين: {users_count}\n")
                    
                    cursor.execute("SELECT COUNT(*) FROM task")
                    tasks_count = cursor.fetchone()[0]
                    f.write(f"عدد المهام: {tasks_count}\n")
                    
                except sqlite3.OperationalError:
                    f.write("تعذر قراءة إحصائيات قاعدة البيانات\n")
                
                conn.close()
        
        print("✅ تم إنشاء ملف معلومات النسخة الاحتياطية")
        
        # ضغط النسخة الاحتياطية
        zip_filename = f"{backup_dir}.zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ تم ضغط النسخة الاحتياطية: {zip_filename}")
        
        # حذف المجلد المؤقت
        shutil.rmtree(backup_dir)
        
        # حساب حجم الملف المضغوط
        file_size = os.path.getsize(zip_filename)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"🎉 تم إنشاء النسخة الاحتياطية بنجاح!")
        print(f"📦 اسم الملف: {zip_filename}")
        print(f"📏 حجم الملف: {file_size_mb:.2f} ميجابايت")
        
        return zip_filename
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
        return None

def restore_achievements(backup_file):
    """استعادة ملفات الإنجاز من النسخة الاحتياطية"""
    
    if not os.path.exists(backup_file):
        print(f"❌ ملف النسخة الاحتياطية غير موجود: {backup_file}")
        return False
    
    print(f"🔄 بدء استعادة النسخة الاحتياطية من: {backup_file}")
    
    try:
        # إنشاء مجلد مؤقت للاستخراج
        temp_dir = "temp_restore"
        os.makedirs(temp_dir, exist_ok=True)
        
        # استخراج الملفات
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        print("✅ تم استخراج الملفات")
        
        # استعادة قاعدة البيانات
        db_backup = os.path.join(temp_dir, 'tasks.db')
        if os.path.exists(db_backup):
            if os.path.exists('tasks.db'):
                # إنشاء نسخة احتياطية من قاعدة البيانات الحالية
                current_backup = f"tasks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2('tasks.db', current_backup)
                print(f"✅ تم حفظ نسخة احتياطية من قاعدة البيانات الحالية: {current_backup}")
            
            shutil.copy2(db_backup, 'tasks.db')
            print("✅ تم استعادة قاعدة البيانات")
        
        # استعادة مجلد الملفات
        uploads_backup = os.path.join(temp_dir, 'uploads')
        if os.path.exists(uploads_backup):
            if os.path.exists('uploads'):
                # إنشاء نسخة احتياطية من مجلد الملفات الحالي
                current_uploads_backup = f"uploads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copytree('uploads', current_uploads_backup)
                print(f"✅ تم حفظ نسخة احتياطية من مجلد الملفات الحالي: {current_uploads_backup}")
                
                # حذف المجلد الحالي
                shutil.rmtree('uploads')
            
            shutil.copytree(uploads_backup, 'uploads')
            print("✅ تم استعادة مجلد الملفات")
        
        # حذف المجلد المؤقت
        shutil.rmtree(temp_dir)
        
        print("🎉 تم استعادة النسخة الاحتياطية بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في استعادة النسخة الاحتياطية: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("💾 نظام النسخ الاحتياطي لملفات الإنجاز")
    print("   مركز الموهوبين بحائل")
    print("   بواسطة: دكتورنت by DrNeT")
    print("=" * 60)
    
    while True:
        print("\n📋 الخيارات المتاحة:")
        print("1. إنشاء نسخة احتياطية")
        print("2. استعادة نسخة احتياطية")
        print("3. خروج")
        
        choice = input("\n🔢 اختر رقم العملية: ").strip()
        
        if choice == '1':
            backup_file = backup_achievements()
            if backup_file:
                print(f"\n💡 نصيحة: احتفظ بالملف {backup_file} في مكان آمن")
        
        elif choice == '2':
            backup_file = input("📁 أدخل مسار ملف النسخة الاحتياطية: ").strip()
            if restore_achievements(backup_file):
                print("\n⚠️  تحذير: يجب إعادة تشغيل التطبيق لتطبيق التغييرات")
        
        elif choice == '3':
            print("👋 وداعاً!")
            break
        
        else:
            print("❌ خيار غير صحيح. يرجى المحاولة مرة أخرى.")