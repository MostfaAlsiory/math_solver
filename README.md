# محلل الاستعلامات العلمية

## التثبيت

1. قم بتنزيل وتثبيت Python (الإصدار 3.8 أو أحدث)
2. قم بإنشاء بيئة افتراضية (اختياري ولكن موصى به):
   ```
   python -m venv venv
   source venv/bin/activate  # لينكس/ماك
   venv\Scripts\activate    # ويندوز
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
# math_solver
