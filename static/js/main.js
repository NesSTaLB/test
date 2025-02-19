// وظائف مساعدة
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(amount);
};

const formatDate = (date) => {
    return new Intl.DateTimeFormat('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
};

// إدارة النماذج
const handleFormSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) {
            throw new Error('حدث خطأ في إرسال النموذج');
        }
        
        const data = await response.json();
        showNotification('success', 'تم حفظ البيانات بنجاح');
        
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    } catch (error) {
        showNotification('error', error.message);
    }
};

// إدارة الإشعارات
const showNotification = (type, message) => {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.notifications-container') || document.body;
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
};

// وظائف AJAX
const fetchData = async (url, options = {}) => {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error('فشل في جلب البيانات');
        }
        
        return await response.json();
    } catch (error) {
        showNotification('error', error.message);
        throw error;
    }
};

// إدارة لوحة التحكم
const initializeDashboard = () => {
    // تحديث البيانات كل دقيقة
    setInterval(updateDashboardData, 60000);
    
    // تهيئة الرسوم البيانية
    initializeCharts();
};

const updateDashboardData = async () => {
    try {
        const data = await fetchData('/api/dashboard/summary/');
        updateDashboardWidgets(data);
    } catch (error) {
        console.error('فشل في تحديث البيانات:', error);
    }
};

const updateDashboardWidgets = (data) => {
    // تحديث الإحصائيات
    Object.entries(data.stats).forEach(([key, value]) => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            element.textContent = value;
        }
    });
    
    // تحديث الرسوم البيانية
    if (window.dashboardCharts) {
        Object.entries(window.dashboardCharts).forEach(([chartId, chart]) => {
            const chartData = data.charts[chartId];
            if (chartData) {
                updateChart(chart, chartData);
            }
        });
    }
};

// إدارة الجداول
const initializeDataTables = () => {
    document.querySelectorAll('.data-table').forEach(table => {
        const options = {
            language: {
                url: '/static/js/dataTables.arabic.json'
            },
            responsive: true,
            ordering: true,
            pageLength: 10
        };
        
        new DataTable(table, options);
    });
};

// وظائف مساعدة
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// تهيئة التطبيق
document.addEventListener('DOMContentLoaded', () => {
    // تهيئة النماذج
    document.querySelectorAll('form[data-ajax]').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // تهيئة الجداول
    initializeDataTables();
    
    // تهيئة لوحة التحكم إذا كانت موجودة
    if (document.querySelector('.dashboard')) {
        initializeDashboard();
    }
    
    // تهيئة tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        new Tooltip(tooltip);
    });
});