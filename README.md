# نظام إدارة الأعمال المتكامل

نظام متكامل لإدارة الأعمال يشمل إدارة المشاريع، المبيعات، المشتريات، وإدارة علاقات العملاء.

## المميزات الرئيسية

- إدارة المشاريع والمهام
- نظام المبيعات والمخزون
- نظام المشتريات وإدارة الموردين
- إدارة علاقات العملاء (CRM)
- لوحة تحكم تفاعلية
- نظام تقارير متقدم
- نظام صلاحيات متعدد المستويات
- واجهة مستخدم عربية بالكامل

## المتطلبات الأساسية

- Python 3.8+
- PostgreSQL 12+
- Redis Server
- Node.js 14+ (للتطوير)

## التثبيت

1. إنشاء بيئة افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

2. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

3. إعداد ملف البيئة:
```bash
cp .env.example .env
# قم بتعديل الإعدادات في ملف .env
```

4. تهيئة قاعدة البيانات:
```bash
python manage.py migrate
```

5. إنشاء مستخدم المشرف:
```bash
python manage.py createsuperuser
```

## التشغيل

1. تشغيل الخادم:
```bash
python manage.py runserver
```

2. تشغيل Celery للمهام الخلفية:
```bash
celery -A management_system worker -l info
```

3. تشغيل Celery Beat للمهام المجدولة:
```bash
celery -A management_system beat -l info
```

## الوصول للنظام

- لوحة التحكم: http://localhost:8000/
- لوحة الإدارة: http://localhost:8000/admin/
- توثيق API: http://localhost:8000/api/docs/

## التطوير

1. تثبيت متطلبات التطوير:
```bash
pip install -r requirements-dev.txt
```

2. تشغيل الاختبارات:
```bash
python manage.py test
```

3. تشغيل فحص الجودة:
```bash
flake8
black .
```

## النسخ الاحتياطي

يتم عمل نسخ احتياطي يومي لقاعدة البيانات والملفات المرفوعة. يمكن استعادة النسخ الاحتياطي باستخدام:

```bash
python manage.py restore_backup backup_file.zip
```

## المساهمة

1. قم بعمل Fork للمشروع
2. قم بإنشاء فرع جديد (`git checkout -b feature/amazing_feature`)
3. قم بإجراء التعديلات
4. قم بعمل Commit (`git commit -m 'إضافة ميزة جديدة'`)
5. قم برفع التغييرات (`git push origin feature/amazing_feature`)
6. قم بإنشاء طلب Pull Request

## الترخيص

هذا المشروع مرخص تحت MIT License - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## الدعم

للمساعدة والدعم الفني، يرجى:
- فتح issue على GitHub
- التواصل عبر البريد الإلكتروني: support@example.com
- زيارة [وثائق المشروع](http://localhost:8000/docs/)# test
