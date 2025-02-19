document.addEventListener('DOMContentLoaded', function() {
    // تحسين معاينة الملفات
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const preview = input.closest('.file-upload-wrapper').querySelector('.file-preview');
        
        input.addEventListener('change', function() {
            preview.innerHTML = '';
            Array.from(this.files).forEach(file => {
                const filePreview = document.createElement('div');
                filePreview.className = 'file-item';
                
                if (file.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.className = 'file-thumbnail';
                    filePreview.appendChild(img);
                }
                
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                fileInfo.innerHTML = `
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                `;
                filePreview.appendChild(fileInfo);
                preview.appendChild(filePreview);
            });
        });
    });

    // تنسيق حجم الملف
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // تحسين حقول التاريخ
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'date-picker-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // إضافة أزرار سريعة للتاريخ
        const quickDates = document.createElement('div');
        quickDates.className = 'quick-dates';
        
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const nextWeek = new Date(today);
        nextWeek.setDate(nextWeek.getDate() + 7);
        
        const quickDateButtons = [
            { text: 'اليوم', date: today },
            { text: 'غداً', date: tomorrow },
            { text: 'أسبوع', date: nextWeek }
        ];

        quickDateButtons.forEach(btn => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'quick-date-btn';
            button.textContent = btn.text;
            button.addEventListener('click', () => {
                input.value = formatDate(btn.date);
                input.dispatchEvent(new Event('change'));
            });
            quickDates.appendChild(button);
        });

        wrapper.appendChild(quickDates);
    });

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    // تحسين الحقول المطلوبة
    const requiredFields = document.querySelectorAll('.field-wrapper.required input, .field-wrapper.required select, .field-wrapper.required textarea');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            const wrapper = this.closest('.field-wrapper');
            wrapper.classList.remove('error');
        });
    });

    function validateField(field) {
        const wrapper = field.closest('.field-wrapper');
        if (!field.value) {
            wrapper.classList.add('error');
            
            // إضافة رسالة خطأ إذا لم تكن موجودة
            if (!wrapper.querySelector('.errorlist')) {
                const errorList = document.createElement('ul');
                errorList.className = 'errorlist';
                const errorItem = document.createElement('li');
                errorItem.textContent = 'هذا الحقل مطلوب.';
                errorList.appendChild(errorItem);
                wrapper.querySelector('.field-input').appendChild(errorList);
            }
        } else {
            wrapper.classList.remove('error');
            const errorList = wrapper.querySelector('.errorlist');
            if (errorList) {
                errorList.remove();
            }
        }
    }

    // تحسين عرض المساعدة
    const helpTexts = document.querySelectorAll('.help');
    helpTexts.forEach(help => {
        const helpIcon = document.createElement('span');
        helpIcon.className = 'help-icon';
        helpIcon.textContent = '?';
        
        const helpContent = help.textContent;
        help.textContent = '';
        help.appendChild(helpIcon);
        
        const tooltip = document.createElement('span');
        tooltip.className = 'help-tooltip';
        tooltip.textContent = helpContent;
        help.appendChild(tooltip);
        
        helpIcon.addEventListener('mouseenter', () => {
            tooltip.style.display = 'block';
        });
        
        helpIcon.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    });

    // تحسين حقول التاريخ
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        field.addEventListener('change', function() {
            validateDates();
        });
    });

    // التحقق من تواريخ المشروع
    function validateDates() {
        const startDate = document.querySelector('input[name="start_date"]');
        const endDate = document.querySelector('input[name="end_date"]');
        
        if (startDate && endDate && startDate.value && endDate.value) {
            if (new Date(endDate.value) < new Date(startDate.value)) {
                endDate.setCustomValidity('تاريخ الانتهاء يجب أن يكون بعد تاريخ البدء');
            } else {
                endDate.setCustomValidity('');
            }
        }
    }

    // تحسين حقل الوصف
    const descField = document.querySelector('textarea[name="description"]');
    if (descField) {
        descField.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight + 2) + 'px';
        });
    }

    // تحسين اختيار الفريق
    const teamSelect = document.querySelector('.field-team_members select');
    if (teamSelect) {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'بحث عن أعضاء الفريق...';
        searchInput.className = 'team-search';
        teamSelect.parentNode.insertBefore(searchInput, teamSelect);

        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            Array.from(teamSelect.options).forEach(option => {
                const text = option.text.toLowerCase();
                option.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // تحسين حقل الحالة
    const statusField = document.querySelector('select[name="status"]');
    if (statusField) {
        statusField.addEventListener('change', function() {
            updateFormBasedOnStatus(this.value);
        });
    }

    function updateFormBasedOnStatus(status) {
        const progressSection = document.querySelector('.field-get_progress');
        if (progressSection) {
            progressSection.style.opacity = status === 'completed' ? '1' : '0.5';
        }

        // إظهار/إخفاء حقول إضافية بناءً على الحالة
        const additionalFields = document.querySelectorAll('.status-dependent');
        additionalFields.forEach(field => {
            field.style.display = status === 'completed' ? 'none' : 'block';
        });
    }

    // تحسين عرض الصور
    const imagePreview = document.querySelector('.field-project_images');
    if (imagePreview) {
        const input = imagePreview.querySelector('input[type="file"]');
        const preview = document.createElement('div');
        preview.className = 'image-preview';
        imagePreview.appendChild(preview);

        input.addEventListener('change', function() {
            preview.innerHTML = '';
            Array.from(this.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.className = 'preview-thumbnail';
                    preview.appendChild(img);
                }
            });
        });
    }

    // تحسين التفاعل مع النموذج
    const form = document.querySelector('#project_form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('يرجى ملء جميع الحقول المطلوبة');
            }
        });
    }
});