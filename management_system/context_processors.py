from django.conf import settings

def admin_branding(request):
    if request.path.startswith('/admin/'):
        return {
            'custom_brand_name': settings.ADMIN_SITE_HEADER,
            'primary_color': getattr(settings, 'ADMIN_PRIMARY_COLOR', '#714B67'),
            'secondary_color': getattr(settings, 'ADMIN_SECONDARY_COLOR', '#00A09D'),
            'rtl_mode': getattr(settings, 'LANGUAGE_CODE', 'en').startswith('ar'),
        }
    return {}