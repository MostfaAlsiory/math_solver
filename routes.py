import os
import logging
import zipfile
import io
import shutil
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Query
from utils.gemini_processor import process_with_gemini
from utils.wolfram_processor import process_with_wolfram
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            flash('جميع الحقول مطلوبة', 'danger')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('كلمات المرور غير متطابقة', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | 
                                          (User.email == email)).first()
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            db.session.rollback()
            flash('حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/history')
@login_required
def history():
    queries = Query.query.filter_by(user_id=current_user.id).order_by(Query.created_at.desc()).all()
    return render_template('history.html', queries=queries)

@app.route('/process_query', methods=['POST'])
@login_required
def process_query():
    try:
        # Get the natural language query from the form
        original_query = request.form.get('query')
        
        if not original_query:
            return jsonify({
                'status': 'error', 
                'message': 'الاستعلام مطلوب'
            }), 400
        
        # Process the query with Google Gemini
        processed_query = process_with_gemini(original_query)
        
        if not processed_query:
            return jsonify({
                'status': 'error', 
                'message': 'فشل في معالجة الاستعلام باستخدام Gemini'
            }), 500
        
        # Process with Wolfram Alpha
        wolfram_result = process_with_wolfram(processed_query)
        
        if not wolfram_result:
            return jsonify({
                'status': 'error', 
                'message': 'فشل في الحصول على نتائج من Wolfram Alpha'
            }), 500
        
        # Create a new query record
        new_query = Query(
            user_id=current_user.id,
            original_query=original_query,
            processed_query=processed_query,
            result=wolfram_result.get('result'),
            result_type=wolfram_result.get('result_type', 'text')
        )
        
        db.session.add(new_query)
        db.session.commit()
        
        response_data = {
            'status': 'success',
            'original_query': original_query,
            'processed_query': processed_query,
            'result': wolfram_result.get('result'),
            'result_type': wolfram_result.get('result_type', 'text')
        }
        
        # If we have rich data, include it in the response
        if wolfram_result.get('result_type') == 'rich' and 'rich_data' in wolfram_result:
            response_data['rich_data'] = wolfram_result.get('rich_data')
            
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء معالجة الاستعلام'
        }), 500

@app.route('/download_project')
def download_project():
    """
    تنزيل المشروع بالكامل كملف ZIP للاستخدام المحلي
    """
    try:
        # إنشاء ملف ZIP في الذاكرة
        memory_file = io.BytesIO()
        
        # إنشاء ملف zip وإضافة الملفات الأساسية فقط
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # الملفات المهمة للنسخة المحلية
            essential_files = [
                'app.py', 'main.py', 'models.py', 'routes.py',
                'utils/gemini_processor.py', 'utils/wolfram_processor.py', 'utils/math_translator.py'
            ]
            
            # إضافة الملفات الأساسية
            for file_path in essential_files:
                try:
                    if os.path.exists(file_path):
                        # تحديد اسم الملف في الأرشيف
                        info = zipfile.ZipInfo(file_path)
                        info.date_time = (2025, 4, 23, 12, 0, 0)
                        info.external_attr = 0o644 << 16
                        
                        # قراءة محتوى الملف وإضافته للأرشيف
                        with open(file_path, 'rb') as f:
                            zf.writestr(info, f.read())
                except Exception as e:
                    logger.warning(f"خطأ في إضافة الملف {file_path}: {e}")
            
            # إضافة مجلدات الواجهة
            for folder in ['templates', 'static']:
                if os.path.exists(folder):
                    for root, _, files in os.walk(folder):
                        for file in files:
                            # تحضير مسار الملف
                            file_path = os.path.join(root, file)
                            
                            # تخطي الملفات غير المطلوبة
                            if file.startswith('.') or file.endswith(('.pyc', '.pyo')):
                                continue
                            
                            try:
                                # إضافة الملف إلى الأرشيف
                                info = zipfile.ZipInfo(file_path)
                                info.date_time = (2025, 4, 23, 12, 0, 0)
                                info.external_attr = 0o644 << 16
                                
                                with open(file_path, 'rb') as f:
                                    zf.writestr(info, f.read())
                            except Exception as e:
                                logger.warning(f"خطأ في إضافة الملف {file_path}: {e}")
            
            # إضافة ملف README.md بتعليمات التثبيت
            readme_content = """# محلل الاستعلامات العلمية

## التثبيت

1. قم بتنزيل وتثبيت Python (الإصدار 3.8 أو أحدث)
2. قم بإنشاء بيئة افتراضية (اختياري ولكن موصى به):
   ```
   python -m venv venv
   source venv/bin/activate  # لينكس/ماك
   venv\\Scripts\\activate    # ويندوز
   ```
3. قم بتثبيت المكتبات المطلوبة:
   ```
   pip install -r requirements.txt
   ```
4. قم بإنشاء ملف `.env` في المجلد الرئيسي وأضف مفاتيح API الخاصة بك:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   WOLFRAM_APP_ID=APPID_FROM_WOLFRAM_ALPHA
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```
5. قم بتشغيل الخادم المحلي:
   ```
   flask run
   ```
6. افتح المتصفح وانتقل إلى `http://localhost:5000`

## الميزات

- تحويل الاستعلامات الطبيعية (بما في ذلك اللغة العربية) إلى استعلامات Wolfram Alpha دقيقة
- دعم الرموز الرياضية باللغة العربية
- تصور المعادلات والرسوم البيانية والنتائج
- تسجيل الاستعلامات وتاريخ نتائجها
- واجهة مستخدم جميلة وسهلة الاستخدام
"""
            zf.writestr('README.md', readme_content)
            
            # إنشاء ملف requirements.txt يحتوي على جميع المكتبات المطلوبة
            requirements = """flask==2.3.3
flask-login==0.6.2
flask-sqlalchemy==3.1.1
gunicorn==21.2.0
email-validator==2.1.1
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.0
werkzeug==2.3.7
sqlalchemy==2.0.25
"""
            zf.writestr('requirements.txt', requirements)
        
        # إعادة تعيين مؤشر الملف إلى البداية
        memory_file.seek(0)
        
        # إرسال الملف للمستخدم
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='scientific_query_processor.zip'
        )
        
    except Exception as e:
        logger.error(f"Error creating ZIP file: {e}")
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء إنشاء ملف ZIP'
        }), 500
