from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from functools import wraps
import uuid

# إضافة datetime إلى السياق العام للقوالب
def inject_datetime():
    return dict(datetime=datetime)

app = Flask(__name__)

# إعدادات قاعدة البيانات السحابية
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# استخدام متغيرات البيئة للإعدادات الحساسة
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# دعم قواعد البيانات المتعددة
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # إصلاح مشكلة postgres:// في Heroku
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # استخدام SQLite محلياً
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_management.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعدادات رفع الملفات
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

# إنشاء مجلد الرفع إذا لم يكن موجوداً
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# دوال مساعدة للقوالب
def get_file_icon(filename):
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    icon_map = {
        'pdf': 'fas fa-file-pdf text-danger',
        'doc': 'fas fa-file-word text-primary',
        'docx': 'fas fa-file-word text-primary',
        'xls': 'fas fa-file-excel text-success',
        'xlsx': 'fas fa-file-excel text-success',
        'ppt': 'fas fa-file-powerpoint text-warning',
        'pptx': 'fas fa-file-powerpoint text-warning',
        'jpg': 'fas fa-file-image text-info',
        'jpeg': 'fas fa-file-image text-info',
        'png': 'fas fa-file-image text-info',
        'gif': 'fas fa-file-image text-info',
        'txt': 'fas fa-file-alt text-secondary'
    }
    return icon_map.get(extension, 'fas fa-file text-secondary')

def format_file_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

# تسجيل دوال السياق
app.context_processor(inject_datetime)
app.jinja_env.globals.update(get_file_icon=get_file_icon)
app.jinja_env.globals.update(format_file_size=format_file_size)

# نماذج قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # مدير، وكيل، معلم موهوبين، إداري
    department = db.Column(db.String(100), nullable=False)  # وحدة العمل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assignee', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='متوسط')  # عالي، متوسط، منخفض
    status = db.Column(db.String(50), nullable=False, default='جديد')  # جديد، قيد التنفيذ، مكتمل، متأخر، ملغي
    department = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # المفاتيح الخارجية
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # العلاقات
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic', cascade='all, delete-orphan')

class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # المفاتيح الخارجية
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # العلاقات
    user = db.relationship('User', backref='comments')

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    achievement_type = db.Column(db.String(50), nullable=False)  # شهادة، جائزة، إنجاز، دورة
    date_achieved = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # المفاتيح الخارجية
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # العلاقات
    user = db.relationship('User', backref='achievements')
    files = db.relationship('AchievementFile', backref='achievement', lazy='dynamic', cascade='all, delete-orphan')

class AchievementFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # المفاتيح الخارجية
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # العلاقات
    uploader = db.relationship('User', backref='uploaded_files')

# دالة للتحقق من امتدادات الملفات المسموحة
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# دالة للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# دالة للتحقق من الصلاحيات
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# الصفحة الرئيسية
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            flash(f'مرحباً {user.full_name}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

# تسجيل مستخدم جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form['role']
        department = request.form['department']
        
        # التحقق من عدم وجود المستخدم
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود بالفعل', 'error')
            return render_template('register.html')
        
        # إنشاء المستخدم الجديد
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            department=department
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

# لوحة التحكم
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # إحصائيات المهام
    total_tasks = Task.query.filter_by(assigned_to=user.id).count()
    pending_tasks = Task.query.filter_by(assigned_to=user.id, status='قيد التنفيذ').count()
    completed_tasks = Task.query.filter_by(assigned_to=user.id, status='مكتمل').count()
    overdue_tasks = Task.query.filter(
        Task.assigned_to == user.id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'مكتمل'
    ).count()
    
    # المهام الحديثة
    recent_tasks = Task.query.filter_by(assigned_to=user.id).order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=user,
                         total_tasks=total_tasks,
                         pending_tasks=pending_tasks,
                         completed_tasks=completed_tasks,
                         overdue_tasks=overdue_tasks,
                         recent_tasks=recent_tasks)

# عرض المهام
@app.route('/tasks')
@login_required
def tasks():
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    query = Task.query
    
    # تطبيق الفلاتر حسب الدور
    if user.role not in ['مدير']:
        query = query.filter_by(assigned_to=user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    tasks = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('tasks.html', tasks=tasks, 
                         status_filter=status_filter, 
                         priority_filter=priority_filter)

# إنشاء مهمة جديدة
@app.route('/tasks/new', methods=['GET', 'POST'])
@login_required
@role_required(['مدير', 'وكيل'])
def new_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        department = request.form['department']
        assigned_to = request.form.get('assigned_to')
        due_date_str = request.form.get('due_date')
        
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            department=department,
            assigned_to=assigned_to if assigned_to else None,
            due_date=due_date,
            created_by=session['user_id']
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('تم إنشاء المهمة بنجاح', 'success')
        return redirect(url_for('tasks'))
    
    # جلب المستخدمين للتعيين
    users = User.query.filter_by(is_active=True).all()
    return render_template('new_task.html', users=users)

# تحديث حالة المهمة
@app.route('/tasks/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    user = User.query.get(session['user_id'])
    
    # التحقق من الصلاحيات
    if task.assigned_to != user.id and user.role not in ['مدير', 'وكيل']:
        flash('ليس لديك صلاحية لتحديث هذه المهمة', 'error')
        return redirect(url_for('tasks'))
    
    new_status = request.form['status']
    task.status = new_status
    task.updated_at = datetime.utcnow()
    
    if new_status == 'مكتمل':
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    flash('تم تحديث حالة المهمة بنجاح', 'success')
    return redirect(url_for('tasks'))

# التقارير
@app.route('/reports')
@login_required
@role_required(['مدير', 'وكيل'])
def reports():
    # إحصائيات عامة
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status='مكتمل').count()
    pending_tasks = Task.query.filter_by(status='قيد التنفيذ').count()
    overdue_tasks = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'مكتمل'
    ).count()
    
    # إحصائيات حسب الوحدة
    departments = ['وحدة الإدارة', 'وحدة العلاقات العامة والإعلام', 
                  'وحدة البرامج الإثرائية', 'وحدة المسابقات', 'وحدة شؤون الطلاب']
    
    dept_stats = {}
    for dept in departments:
        dept_stats[dept] = {
            'total': Task.query.filter_by(department=dept).count(),
            'completed': Task.query.filter_by(department=dept, status='مكتمل').count(),
            'pending': Task.query.filter_by(department=dept, status='قيد التنفيذ').count()
        }
    
    # أداء المستخدمين
    users_performance = []
    users = User.query.filter_by(is_active=True).all()
    for user in users:
        user_tasks = Task.query.filter_by(assigned_to=user.id).count()
        user_completed = Task.query.filter_by(assigned_to=user.id, status='مكتمل').count()
        completion_rate = (user_completed / user_tasks * 100) if user_tasks > 0 else 0
        
        users_performance.append({
            'user': user,
            'total_tasks': user_tasks,
            'completed_tasks': user_completed,
            'completion_rate': round(completion_rate, 1)
        })
    
    return render_template('reports.html',
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         pending_tasks=pending_tasks,
                         overdue_tasks=overdue_tasks,
                         dept_stats=dept_stats,
                         users_performance=users_performance)

# صفحة الملف الشخصي
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    # إضافة إحصائيات المهام
    user.total_tasks = Task.query.filter_by(assigned_to=user.id).count()
    user.completed_tasks = Task.query.filter_by(assigned_to=user.id, status='مكتمل').count()
    return render_template('profile.html', user=user)

# تغيير كلمة المرور
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        user = User.query.get(session['user_id'])
        
        # التحقق من كلمة المرور الحالية
        if not check_password_hash(user.password_hash, current_password):
            flash('كلمة المرور الحالية غير صحيحة', 'error')
            return render_template('change_password.html')
        
        # التحقق من تطابق كلمة المرور الجديدة
        if new_password != confirm_password:
            flash('كلمة المرور الجديدة غير متطابقة', 'error')
            return render_template('change_password.html')
        
        # التحقق من طول كلمة المرور
        if len(new_password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('change_password.html')
        
        # تحديث كلمة المرور
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')

# إدارة المستخدمين (للمدير فقط)
@app.route('/manage_users')
@login_required
@role_required(['مدير'])
def manage_users():
    users = User.query.all()
    # إضافة عدد المهام لكل مستخدم
    for user in users:
        user.task_count = Task.query.filter_by(assigned_to=user.id).count()
    return render_template('manage_users.html', users=users)

# حذف مستخدم (للمدير فقط)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required(['مدير'])
def delete_user(user_id):
    # منع المدير من حذف نفسه
    if user_id == session['user_id']:
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    # التحقق من وجود مهام مرتبطة بالمستخدم
    user_tasks = Task.query.filter_by(assigned_to=user_id).count()
    
    if user_tasks > 0:
        # إلغاء تعيين المهام بدلاً من حذف المستخدم
        flash(f'المستخدم {user.full_name} لديه {user_tasks} مهمة مرتبطة. يرجى إعادة تعيين المهام أولاً أو إلغاء تفعيل الحساب.', 'warning')
        return redirect(url_for('manage_users'))
    
    # حذف المستخدم
    username = user.username
    full_name = user.full_name
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'تم حذف المستخدم {full_name} ({username}) بنجاح', 'success')
    return redirect(url_for('manage_users'))

# تفعيل/إلغاء تفعيل مستخدم (للمدير فقط)
@app.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
@role_required(['مدير'])
def toggle_user_status(user_id):
    # منع المدير من إلغاء تفعيل نفسه
    if user_id == session['user_id']:
        flash('لا يمكنك إلغاء تفعيل حسابك الخاص', 'error')
        return redirect(url_for('manage_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    
    db.session.commit()
    
    status = 'تم تفعيل' if user.is_active else 'تم إلغاء تفعيل'
    flash(f'{status} حساب {user.full_name} بنجاح', 'success')
    
    return redirect(url_for('manage_users'))

# إعادة تعيين كلمة مرور مستخدم (للمدير فقط)
@app.route('/reset_user_password/<int:user_id>', methods=['POST'])
@login_required
@role_required(['مدير'])
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # كلمة مرور افتراضية جديدة
    new_password = 'password123'
    user.password_hash = generate_password_hash(new_password)
    
    db.session.commit()
    
    flash(f'تم إعادة تعيين كلمة مرور {user.full_name}. كلمة المرور الجديدة: {new_password}', 'info')
    return redirect(url_for('manage_users'))

# ملف الإنجاز - عرض الإنجازات
@app.route('/achievements')
@login_required
def achievements():
    user = User.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    achievement_type_filter = request.args.get('type', '')
    
    query = Achievement.query.filter_by(user_id=user.id)
    
    if achievement_type_filter:
        query = query.filter_by(achievement_type=achievement_type_filter)
    
    achievements = query.order_by(Achievement.date_achieved.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('achievements.html', 
                         achievements=achievements, 
                         type_filter=achievement_type_filter)

# ملف الإنجاز - إضافة إنجاز جديد
@app.route('/achievements/new', methods=['GET', 'POST'])
@login_required
def new_achievement():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        achievement_type = request.form['achievement_type']
        date_achieved_str = request.form['date_achieved']
        
        date_achieved = datetime.strptime(date_achieved_str, '%Y-%m-%d')
        
        achievement = Achievement(
            title=title,
            description=description,
            achievement_type=achievement_type,
            date_achieved=date_achieved,
            user_id=session['user_id']
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        # رفع الملفات إن وجدت
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    # إنشاء اسم ملف فريد
                    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # حفظ معلومات الملف في قاعدة البيانات
                    achievement_file = AchievementFile(
                        filename=filename,
                        original_filename=file.filename,
                        file_path=file_path,
                        file_size=os.path.getsize(file_path),
                        file_type=file.filename.rsplit('.', 1)[1].lower(),
                        achievement_id=achievement.id,
                        uploaded_by=session['user_id']
                    )
                    db.session.add(achievement_file)
            
            db.session.commit()
        
        flash('تم إضافة الإنجاز بنجاح', 'success')
        return redirect(url_for('achievements'))
    
    return render_template('new_achievement.html')

# ملف الإنجاز - تعديل إنجاز
@app.route('/achievements/<int:achievement_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # التحقق من الصلاحيات
    if achievement.user_id != session['user_id']:
        flash('ليس لديك صلاحية لتعديل هذا الإنجاز', 'error')
        return redirect(url_for('achievements'))
    
    if request.method == 'POST':
        achievement.title = request.form['title']
        achievement.description = request.form['description']
        achievement.achievement_type = request.form['achievement_type']
        achievement.date_achieved = datetime.strptime(request.form['date_achieved'], '%Y-%m-%d')
        achievement.updated_at = datetime.utcnow()
        
        # رفع ملفات جديدة إن وجدت
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    achievement_file = AchievementFile(
                        filename=filename,
                        original_filename=file.filename,
                        file_path=file_path,
                        file_size=os.path.getsize(file_path),
                        file_type=file.filename.rsplit('.', 1)[1].lower(),
                        achievement_id=achievement.id,
                        uploaded_by=session['user_id']
                    )
                    db.session.add(achievement_file)
        
        db.session.commit()
        flash('تم تحديث الإنجاز بنجاح', 'success')
        return redirect(url_for('achievements'))
    
    return render_template('edit_achievement.html', achievement=achievement)

# ملف الإنجاز - حذف إنجاز
@app.route('/achievements/<int:achievement_id>/delete', methods=['POST'])
@login_required
def delete_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # التحقق من الصلاحيات
    if achievement.user_id != session['user_id']:
        flash('ليس لديك صلاحية لحذف هذا الإنجاز', 'error')
        return redirect(url_for('achievements'))
    
    # حذف الملفات المرتبطة
    for file in achievement.files:
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
    
    db.session.delete(achievement)
    db.session.commit()
    
    flash('تم حذف الإنجاز بنجاح', 'success')
    return redirect(url_for('achievements'))

# ملف الإنجاز - حذف ملف
@app.route('/achievements/files/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_achievement_file(file_id):
    file = AchievementFile.query.get_or_404(file_id)
    achievement = file.achievement
    
    # التحقق من الصلاحيات
    if achievement.user_id != session['user_id']:
        flash('ليس لديك صلاحية لحذف هذا الملف', 'error')
        return redirect(url_for('achievements'))
    
    # حذف الملف من النظام
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    db.session.delete(file)
    db.session.commit()
    
    flash('تم حذف الملف بنجاح', 'success')
    return redirect(url_for('edit_achievement', achievement_id=achievement.id))

# ملف الإنجاز - تحميل ملف
@app.route('/achievements/files/<int:file_id>/download')
@login_required
def download_achievement_file(file_id):
    file = AchievementFile.query.get_or_404(file_id)
    achievement = file.achievement
    
    # التحقق من الصلاحيات
    if achievement.user_id != session['user_id']:
        flash('ليس لديك صلاحية لتحميل هذا الملف', 'error')
        return redirect(url_for('achievements'))
    
    return send_file(file.file_path, as_attachment=True, download_name=file.original_filename)

# ملف الإنجاز - طباعة
@app.route('/achievements/print')
@login_required
def print_achievements():
    user = User.query.get(session['user_id'])
    achievements = Achievement.query.filter_by(user_id=user.id).order_by(Achievement.date_achieved.desc()).all()
    
    return render_template('print_achievements.html', user=user, achievements=achievements)

# ===== نظام التحديث التلقائي =====
from auto_updater import updater

# صفحة تحديث النظام
@app.route('/system-update')
@login_required
def system_update():
    # التحقق من صلاحيات المدير
    user = User.query.get(session['user_id'])
    if user.role != 'مدير':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('system_update.html')

# API - فحص التحديثات
@app.route('/api/check-updates')
@login_required
def api_check_updates():
    # التحقق من صلاحيات المدير
    user = User.query.get(session['user_id'])
    if user.role != 'مدير':
        return jsonify({'status': 'error', 'message': 'غير مصرح لك'})
    
    result = updater.check_for_updates()
    return jsonify(result)

# API - تنفيذ التحديث
@app.route('/api/perform-update', methods=['POST'])
@login_required
def api_perform_update():
    # التحقق من صلاحيات المدير
    user = User.query.get(session['user_id'])
    if user.role != 'مدير':
        return jsonify({'status': 'error', 'message': 'غير مصرح لك'})
    
    result = updater.perform_update()
    return jsonify(result)

# API - إنشاء نسخة احتياطية
@app.route('/api/create-backup', methods=['POST'])
@login_required
def api_create_backup():
    # التحقق من صلاحيات المدير
    user = User.query.get(session['user_id'])
    if user.role != 'مدير':
        return jsonify({'status': 'error', 'message': 'غير مصرح لك'})
    
    result = updater.create_backup()
    return jsonify(result)

# API - حالة النظام
@app.route('/api/system-status')
@login_required
def api_system_status():
    # التحقق من صلاحيات المدير
    user = User.query.get(session['user_id'])
    if user.role != 'مدير':
        return jsonify({'status': 'error', 'message': 'غير مصرح لك'})
    
    result = updater.get_system_status()
    return jsonify(result)

# API - فحص صحة التطبيق (للاستخدام الداخلي)
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'دكتورنت by DrNeT'
    })

# إنشاء قاعدة البيانات
def create_tables():
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم مدير افتراضي
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@giftedcenter.edu.sa',
                password_hash=generate_password_hash('admin123'),
                full_name='مدير النظام',
                role='مدير',
                department='وحدة الإدارة'
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)