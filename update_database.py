#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث قاعدة البيانات لإضافة ميزة ملف الإنجاز
مركز الموهوبين بحائل
"""

from app import app, db, Achievement, AchievementFile
import os

def update_database():
    """تحديث قاعدة البيانات بالجداول الجديدة"""
    
    print("🔄 بدء تحديث قاعدة البيانات...")
    
    with app.app_context():
        try:
            # إنشاء الجداول الجديدة
            db.create_all()
            print("✅ تم إنشاء جداول ملف الإنجاز بنجاح")
            
            # التحقق من وجود مجلد الرفع
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                print(f"✅ تم إنشاء مجلد الرفع: {upload_folder}")
            else:
                print(f"✅ مجلد الرفع موجود: {upload_folder}")
            
            # عرض إحصائيات قاعدة البيانات
            achievement_count = Achievement.query.count()
            file_count = AchievementFile.query.count()
            
            print(f"📊 إحصائيات قاعدة البيانات:")
            print(f"   - عدد الإنجازات: {achievement_count}")
            print(f"   - عدد الملفات: {file_count}")
            
            print("🎉 تم تحديث قاعدة البيانات بنجاح!")
            print("\n📋 الميزات الجديدة المتاحة:")
            print("   ✓ إضافة وتعديل وحذف الإنجازات")
            print("   ✓ رفع وإدارة الملفات المرفقة")
            print("   ✓ تصفية الإنجازات حسب النوع")
            print("   ✓ طباعة ملف الإنجاز")
            print("   ✓ أزرار التعديل في جميع الشاشات")
            
        except Exception as e:
            print(f"❌ خطأ في تحديث قاعدة البيانات: {str(e)}")
            return False
    
    return True

def add_sample_data():
    """إضافة بيانات تجريبية (اختياري)"""
    
    print("\n🔄 إضافة بيانات تجريبية...")
    
    with app.app_context():
        try:
            # التحقق من وجود مستخدمين
            from app import User
            users = User.query.all()
            
            if not users:
                print("⚠️  لا توجد مستخدمين في النظام")
                return False
            
            # إضافة إنجاز تجريبي للمستخدم الأول
            user = users[0]
            
            # التحقق من عدم وجود إنجازات مسبقة
            existing_achievements = Achievement.query.filter_by(user_id=user.id).count()
            
            if existing_achievements == 0:
                sample_achievement = Achievement(
                    title="شهادة تقدير للأداء المتميز",
                    description="شهادة تقدير من إدارة المركز للأداء المتميز في العام الدراسي 2024",
                    achievement_type="شهادة",
                    date_achieved=db.func.current_date(),
                    user_id=user.id
                )
                
                db.session.add(sample_achievement)
                db.session.commit()
                
                print(f"✅ تم إضافة إنجاز تجريبي للمستخدم: {user.full_name}")
            else:
                print(f"ℹ️  المستخدم {user.full_name} لديه {existing_achievements} إنجاز مسبقاً")
                
        except Exception as e:
            print(f"❌ خطأ في إضافة البيانات التجريبية: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🏆 تحديث نظام إدارة مهام مركز الموهوبين بحائل")
    print("   إضافة ميزة ملف الإنجاز")
    print("   بواسطة: دكتورنت by DrNeT")
    print("=" * 60)
    
    # تحديث قاعدة البيانات
    if update_database():
        # إضافة بيانات تجريبية (اختياري)
        response = input("\n❓ هل تريد إضافة بيانات تجريبية؟ (y/n): ").lower().strip()
        if response in ['y', 'yes', 'نعم']:
            add_sample_data()
        
        print("\n🎯 التحديث مكتمل! يمكنك الآن:")
        print("   1. تشغيل التطبيق: python app.py")
        print("   2. الدخول إلى النظام")
        print("   3. الوصول لملف الإنجاز من الشريط الجانبي")
        print("\n🌟 استمتع بالميزات الجديدة!")
    else:
        print("\n❌ فشل في التحديث. يرجى مراجعة الأخطاء أعلاه.")