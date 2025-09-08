"""
نظام التحديث التلقائي لمشروع إدارة المهام
Auto Update System for Task Management Project
دكتورنت by DrNeT
"""

import requests
import json
import os
import subprocess
import time
from datetime import datetime
from flask import current_app
import logging

class AutoUpdater:
    def __init__(self):
        self.github_repo = "KSADRNET/mahham"
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}"
        self.railway_app_url = "https://web-production-c090b.up.railway.app"
        self.local_version_file = "version_info.json"
        
    def get_github_latest_commit(self):
        """الحصول على آخر commit من GitHub"""
        try:
            response = requests.get(f"{self.github_api_url}/commits/main", timeout=10)
            if response.status_code == 200:
                commit_data = response.json()
                return {
                    'sha': commit_data['sha'][:7],  # أول 7 أحرف من SHA
                    'message': commit_data['commit']['message'],
                    'date': commit_data['commit']['committer']['date'],
                    'author': commit_data['commit']['author']['name']
                }
            return None
        except Exception as e:
            print(f"خطأ في الحصول على معلومات GitHub: {e}")
            return None
    
    def get_local_version(self):
        """الحصول على النسخة المحلية الحالية"""
        try:
            if os.path.exists(self.local_version_file):
                with open(self.local_version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"خطأ في قراءة النسخة المحلية: {e}")
            return None
    
    def save_local_version(self, version_info):
        """حفظ معلومات النسخة المحلية"""
        try:
            with open(self.local_version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"خطأ في حفظ النسخة المحلية: {e}")
            return False
    
    def check_for_updates(self):
        """التحقق من وجود تحديثات"""
        github_version = self.get_github_latest_commit()
        local_version = self.get_local_version()
        
        if not github_version:
            return {
                'status': 'error',
                'message': 'فشل في الاتصال بـ GitHub'
            }
        
        if not local_version:
            # أول مرة - حفظ النسخة الحالية
            self.save_local_version({
                'current_commit': github_version['sha'],
                'last_check': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            })
            return {
                'status': 'initialized',
                'message': 'تم تهيئة نظام التحديث',
                'current_version': github_version['sha']
            }
        
        if github_version['sha'] != local_version.get('current_commit'):
            return {
                'status': 'update_available',
                'message': 'يوجد تحديث جديد متاح',
                'current_version': local_version.get('current_commit'),
                'new_version': github_version['sha'],
                'commit_message': github_version['message'],
                'commit_date': github_version['date']
            }
        
        return {
            'status': 'up_to_date',
            'message': 'البرنامج محدث لآخر إصدار',
            'current_version': github_version['sha']
        }
    
    def trigger_railway_deploy(self):
        """محاولة تحفيز إعادة النشر في Railway"""
        try:
            # محاولة الوصول للتطبيق لتحفيز إعادة التحميل
            response = requests.get(f"{self.railway_app_url}/health", timeout=30)
            
            # إنشاء ملف trigger لإجبار Railway على إعادة النشر
            trigger_file = "railway_deploy_trigger.txt"
            with open(trigger_file, 'w') as f:
                f.write(f"Deploy triggered at: {datetime.now().isoformat()}")
            
            return {
                'status': 'triggered',
                'message': 'تم تحفيز عملية النشر في Railway'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'فشل في تحفيز النشر: {str(e)}'
            }
    
    def perform_update(self):
        """تنفيذ عملية التحديث"""
        try:
            # التحقق من التحديثات
            update_check = self.check_for_updates()
            
            if update_check['status'] != 'update_available':
                return update_check
            
            # تحفيز إعادة النشر في Railway
            deploy_result = self.trigger_railway_deploy()
            
            # تحديث معلومات النسخة المحلية
            new_version_info = {
                'current_commit': update_check['new_version'],
                'last_check': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat(),
                'deploy_status': deploy_result['status']
            }
            
            self.save_local_version(new_version_info)
            
            return {
                'status': 'updated',
                'message': 'تم تحديث البرنامج بنجاح',
                'new_version': update_check['new_version'],
                'deploy_result': deploy_result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'فشل في التحديث: {str(e)}'
            }
    
    def create_backup(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            from datetime import datetime
            import shutil
            
            # مسار قاعدة البيانات
            db_path = os.path.join('instance', 'task_management.db')
            
            if os.path.exists(db_path):
                # إنشاء اسم النسخة الاحتياطية
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f'task_management_backup_{timestamp}.db'
                backup_path = os.path.join('instance', backup_name)
                
                # نسخ قاعدة البيانات
                shutil.copy2(db_path, backup_path)
                
                return {
                    'status': 'success',
                    'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
                    'backup_file': backup_name
                }
            else:
                return {
                    'status': 'error',
                    'message': 'لم يتم العثور على قاعدة البيانات'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'فشل في إنشاء النسخة الاحتياطية: {str(e)}'
            }
    
    def get_system_status(self):
        """الحصول على حالة النظام الشاملة"""
        try:
            github_info = self.get_github_latest_commit()
            local_info = self.get_local_version()
            update_status = self.check_for_updates()
            
            # فحص حالة Railway
            railway_status = self.check_railway_status()
            
            return {
                'github': github_info,
                'local': local_info,
                'update_status': update_status,
                'railway_status': railway_status,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'فشل في الحصول على حالة النظام: {str(e)}'
            }
    
    def check_railway_status(self):
        """فحص حالة تطبيق Railway"""
        try:
            response = requests.get(self.railway_app_url, timeout=10)
            if response.status_code == 200:
                return {
                    'status': 'online',
                    'message': 'التطبيق يعمل بشكل طبيعي',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'خطأ في الاستجابة: {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'offline',
                'message': f'التطبيق غير متاح: {str(e)}'
            }

# إنشاء مثيل من المحدث
updater = AutoUpdater()