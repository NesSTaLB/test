# Generated by Django 4.2.19 on 2025-02-18 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DashboardWidget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="العنوان")),
                (
                    "widget_type",
                    models.CharField(
                        choices=[
                            ("sales_chart", "رسم بياني للمبيعات"),
                            ("revenue_chart", "رسم بياني للإيرادات"),
                            ("tasks_summary", "ملخص المهام"),
                            ("projects_status", "حالة المشاريع"),
                            ("top_customers", "كبار العملاء"),
                            ("inventory_alerts", "تنبيهات المخزون"),
                        ],
                        max_length=20,
                        verbose_name="نوع العنصر",
                    ),
                ),
                ("position", models.IntegerField(default=0, verbose_name="الترتيب")),
                ("is_active", models.BooleanField(default=True, verbose_name="نشط")),
                (
                    "refresh_interval",
                    models.IntegerField(
                        default=300, verbose_name="فترة التحديث (بالثواني)"
                    ),
                ),
                (
                    "settings",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="الإعدادات"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
            ],
            options={
                "verbose_name": "عنصر لوحة التحكم",
                "verbose_name_plural": "عناصر لوحة التحكم",
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="UserDashboardPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("layout", models.JSONField(default=dict, verbose_name="تخطيط اللوحة")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
            ],
            options={
                "verbose_name": "تفضيلات لوحة التحكم",
                "verbose_name_plural": "تفضيلات لوحة التحكم",
            },
        ),
        migrations.CreateModel(
            name="UserWidgetSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.IntegerField(verbose_name="الموقع")),
                ("is_visible", models.BooleanField(default=True, verbose_name="مرئي")),
                (
                    "settings",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="الإعدادات"
                    ),
                ),
                (
                    "user_preference",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.userdashboardpreference",
                        verbose_name="تفضيلات المستخدم",
                    ),
                ),
                (
                    "widget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.dashboardwidget",
                        verbose_name="العنصر",
                    ),
                ),
            ],
            options={
                "verbose_name": "إعدادات عنصر المستخدم",
                "verbose_name_plural": "إعدادات عناصر المستخدم",
                "ordering": ["position"],
            },
        ),
    ]
