// وظيفة لتنزيل المشروع كملف ZIP
function downloadProject() {
    // إظهار رسالة توضيحية
    showDownloadingMessage();
    
    // طلب تنزيل المشروع من الخادم باستخدام طريقة مباشرة لضمان بدء التنزيل
    try {
        // إنشاء عنصر iframe مخفي للتنزيل بدون التحويل إلى blob
        // هذه الطريقة أكثر موثوقية في البيئات المختلفة
        const downloadFrame = document.createElement('iframe');
        downloadFrame.style.display = 'none';
        downloadFrame.src = '/download_project';
        document.body.appendChild(downloadFrame);
        
        // إظهار رسالة نجاح بعد مهلة قصيرة
        setTimeout(() => {
            // إزالة الإطار بعد بدء التنزيل
            document.body.removeChild(downloadFrame);
            showSuccessMessage();
        }, 1500);
    } catch (error) {
        console.error('Error during download:', error);
        // طريقة بديلة للتنزيل في حالة فشل الطريقة الأولى
        window.location.href = '/download_project';
        showSuccessMessage();
    }
}

// وظيفة لإظهار رسالة "جاري التنزيل"
function showDownloadingMessage() {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    alertContainer.innerHTML = `
        <div class="alert alert-info alert-dismissible fade show rtl" role="alert">
            <i class="fas fa-spinner fa-spin me-2"></i> جاري تحضير وتنزيل المشروع، يرجى الانتظار...
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// وظيفة لإظهار رسالة نجاح
function showSuccessMessage() {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    alertContainer.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show rtl" role="alert">
            <i class="fas fa-check-circle me-2"></i> تم تنزيل المشروع بنجاح!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // إخفاء الرسالة بعد 5 ثوان
    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => alertContainer.innerHTML = '', 300);
        }
    }, 5000);
}

// وظيفة لإظهار رسالة خطأ
function showErrorMessage() {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    alertContainer.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show rtl" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i> حدث خطأ أثناء تنزيل المشروع. يرجى المحاولة مرة أخرى.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}