from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    """
    subject = 'مرحباً بك في نظام إدارة الأعمال'
    html_message = render_to_string('users/email/welcome.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )

def send_password_reset_email(user, reset_url):
    """
    Send password reset email
    """
    subject = 'إعادة تعيين كلمة المرور'
    html_message = render_to_string('users/email/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )

def get_user_permissions(user):
    """
    Get user permissions based on role
    """
    permissions = {
        'admin': {
            'can_manage_users': True,
            'can_manage_roles': True,
            'can_view_reports': True,
            'can_manage_settings': True,
        },
        'manager': {
            'can_manage_users': False,
            'can_manage_roles': False,
            'can_view_reports': True,
            'can_manage_settings': False,
        },
        'employee': {
            'can_manage_users': False,
            'can_manage_roles': False,
            'can_view_reports': False,
            'can_manage_settings': False,
        }
    }
    return permissions.get(user.role, permissions['employee'])