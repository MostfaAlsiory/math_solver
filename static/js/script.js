// Main JavaScript functionality for Scientific Query Processor

document.addEventListener('DOMContentLoaded', function() {
    
    // وظيفة لتنسيق الكسور والأسس وتحسين عرض الصيغ الرياضية
    function formatFractions(text) {
        if (!text) return text;
        
        let formattedText = text;
        
        // تحويل \frac{a}{b} إلى شكل كسر بتنسيق HTML
        const fracRegex = /\$?\\frac\{([^{}]+)\}\{([^{}]+)\}\$?/g;
        formattedText = formattedText.replace(fracRegex, '<div class="fraction"><span class="numerator">$1</span><span class="denominator">$2</span></div>');
        
        // تحويل الكسور العادية a/b إلى شكل كسر بتنسيق HTML (فقط إذا لم تكن جزءًا من تاج HTML)
        const simpleRegex = /(\d+)\/(\d+)(?![^<]*>)/g;
        formattedText = formattedText.replace(simpleRegex, '<div class="fraction"><span class="numerator">$1</span><span class="denominator">$2</span></div>');
        
        // تحويل الأسس مع علامة ^ إلى <sup>
        formattedText = formattedText.replace(/([a-zA-Zأ-ي\d])\^(\d+)(?![^<]*>)/g, '$1<sup>$2</sup>');
        
        // تحويل جذر تربيعي
        formattedText = formattedText.replace(/sqrt\(([^)]+)\)/g, '√($1)');
        
        // تنسيق المعادلات المثلثية
        formattedText = formattedText.replace(/sin\(/g, 'جا(');
        formattedText = formattedText.replace(/cos\(/g, 'جتا(');
        formattedText = formattedText.replace(/tan\(/g, 'ظا(');
        
        // تحسين عرض اللوغاريتمات
        formattedText = formattedText.replace(/log\(/g, 'لو(');
        
        // تحويل المتغيرات الأكثر شيوعًا
        formattedText = formattedText.replace(/\b([^<>]*)x([^<>]*)\b/g, '$1س$2');
        formattedText = formattedText.replace(/\b([^<>]*)y([^<>]*)\b/g, '$1ص$2');
        formattedText = formattedText.replace(/\b([^<>]*)z([^<>]*)\b/g, '$1ع$2');
        
        return formattedText;
    }
    // Handle query form submission
    const queryForm = document.getElementById('query-form');
    const resultContainer = document.getElementById('result-container');
    
    if (queryForm) {
        queryForm.addEventListener('submit', function(event) {
            event.preventDefault();
            processQuery();
        });
    }
    
    // Process and submit query to backend
    function processQuery() {
        const queryInput = document.getElementById('query-input');
        const submitButton = document.getElementById('submit-button');
        const queryText = queryInput.value.trim();
        
        if (!queryText) {
            showAlert('الرجاء إدخال سؤال علمي للمعالجة', 'danger');
            return;
        }
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جارِ المعالجة...';
        
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="text-center my-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">جارِ معالجة استعلامك...</p>
                </div>
            `;
            resultContainer.style.display = 'block';
        }
        
        // Submit form data to the server
        const formData = new FormData(queryForm);
        
        fetch('/process_query', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            submitButton.disabled = false;
            submitButton.innerHTML = 'معالجة الاستعلام';
            
            if (data.status === 'success') {
                displayResults(data);
            } else {
                showAlert(data.message || 'حدث خطأ أثناء معالجة الاستعلام', 'danger');
                if (resultContainer) {
                    resultContainer.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            submitButton.disabled = false;
            submitButton.innerHTML = 'معالجة الاستعلام';
            showAlert('حدث خطأ أثناء الاتصال بالخادم', 'danger');
            
            if (resultContainer) {
                resultContainer.style.display = 'none';
            }
        });
    }
    
    // Display query results
    function displayResults(data) {
        if (!resultContainer) return;
        
        // Format the result with proper styling
        let resultHtml = `
            <div class="result-header">
                <h3 class="rtl">نتيجة الاستعلام</h3>
                <div class="small text-muted rtl">السؤال الأصلي: ${data.original_query}</div>
                <div class="small text-muted rtl">الاستعلام المعالج: ${data.processed_query}</div>
            </div>
            <div class="result-content rtl">
        `;
        
        // Handle different result types
        if (data.result_type === 'rich' && data.rich_data) {
            // Format rich results with images and text
            resultHtml += formatRichResults(data.rich_data);
        } else if (data.result_type === 'text') {
            // Format the text result, handling potential markdown-like structure
            const formattedText = formatResultText(data.result);
            resultHtml += formattedText;
        } else {
            // Fallback for other result types
            resultHtml += `<pre>${data.result}</pre>`;
        }
        
        resultHtml += '</div>';
        resultContainer.innerHTML = resultHtml;
        resultContainer.style.display = 'block';
        
        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Format rich results with text and images
    function formatRichResults(richData) {
        if (!richData || !richData.length) {
            return '<p>لم يتم العثور على نتائج</p>';
        }
        
        let formattedHtml = '<div class="rich-results">';
        
        // Iterate through each pod
        richData.forEach(pod => {
            formattedHtml += `
                <div class="result-pod mb-4">
                    <h4 class="pod-title">${pod.title}</h4>
                    <div class="pod-content">
            `;
            
            // Iterate through subpods
            pod.subpods.forEach(subpod => {
                if (subpod.image) {
                    // If there's an image, display it with text as caption
                    formattedHtml += `
                        <div class="subpod-item mb-3">
                            <div class="text-center">
                                <img src="${subpod.image}" alt="${subpod.text}" class="img-fluid rounded shadow-sm mb-2" />
                            </div>
                    `;
                    
                    if (subpod.text) {
                        // تحديد ما إذا كان النص يحتوي على صيغة رياضية أو كسور
                        const hasMathFormula = /[+\-*/^=]|sin|cos|tan|log|sqrt|جا|جتا|ظا|لو|جذر/.test(subpod.text);
                        const isFraction = /\\frac{.*}{.*}|(\d+)\/(\d+)/.test(subpod.text);
                        const isResult = /النتيجة|الحل|القيمة|=/.test(subpod.text);
                        
                        if (isResult) {
                            // عرض النتيجة النهائية بتنسيق مميز
                            formattedHtml += `<div class="result-final">${formatFractions(subpod.text)}</div>`;
                        } else if (isFraction) {
                            // عرض النص الذي يحتوي على كسور بتنسيق خاص
                            formattedHtml += `<div class="arabic-math math-highlight">${formatFractions(subpod.text)}</div>`;
                        } else if (hasMathFormula) {
                            // عرض الصيغة الرياضية العادية
                            formattedHtml += `<div class="arabic-math"><span class="math-formula">${formatFractions(subpod.text)}</span></div>`;
                        } else {
                            // عرض النص العادي
                            formattedHtml += `<div class="arabic-math">${subpod.text}</div>`;
                        }
                    }
                    
                    formattedHtml += '</div>';
                } else if (subpod.text) {
                    // تحديد ما إذا كان النص يحتوي على صيغة رياضية أو كسور
                    const hasMathFormula = /[+\-*/^=]|sin|cos|tan|log|sqrt|جا|جتا|ظا|لو|جذر/.test(subpod.text);
                    const isFraction = /\\frac{.*}{.*}|(\d+)\/(\d+)/.test(subpod.text);
                    const isResult = /النتيجة|الحل|القيمة|=/.test(subpod.text);
                    
                    formattedHtml += `<div class="subpod-item mb-3">`;
                    
                    if (isResult) {
                        // عرض النتيجة النهائية بتنسيق مميز
                        formattedHtml += `<div class="result-final">${formatFractions(subpod.text)}</div>`;
                    } else if (isFraction) {
                        // عرض النص الذي يحتوي على كسور بتنسيق خاص
                        formattedHtml += `<div class="arabic-math math-highlight">${formatFractions(subpod.text)}</div>`;
                    } else if (hasMathFormula) {
                        // عرض الصيغة الرياضية العادية
                        formattedHtml += `<div class="arabic-math"><span class="math-formula">${formatFractions(subpod.text)}</span></div>`;
                    } else {
                        // عرض النص العادي
                        formattedHtml += `<div class="arabic-math">${subpod.text}</div>`;
                    }
                    
                    formattedHtml += '</div>';
                }
            });
            
            formattedHtml += '</div></div>';
            
            // Add divider between pods except for the last one
            if (richData.indexOf(pod) < richData.length - 1) {
                formattedHtml += '<hr class="pod-divider" />';
            }
        });
        
        formattedHtml += '</div>';
        return formattedHtml;
    }
    
    // Format the text result to handle potential formatting
    function formatResultText(text) {
        if (!text) return '<p>لم يتم العثور على نتائج</p>';
        
        // Replace ** markers with bold tags
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to HTML
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Transform fractions to a nicer representation
        formatted = formatFractions(formatted);
        
        // Wrap mathematical expressions in special formatting
        const hasMathFormula = /[+\-*/^=]|sin|cos|tan|log|sqrt|جا|جتا|ظا|لو|جذر/.test(text);
        if (hasMathFormula) {
            return `<div class="arabic-math"><span class="math-formula">${formatted}</span></div>`;
        }
        
        return formatted;
    }
    
    // Show bootstrap alerts
    function showAlert(message, type) {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show rtl`;
        alertElement.role = 'alert';
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alertElement);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertElement.classList.remove('show');
            setTimeout(() => alertElement.remove(), 300);
        }, 5000);
    }
    
    // For history page: add click event to expand/collapse history items
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        const header = item.querySelector('.history-query');
        const content = item.querySelector('.history-result');
        
        if (header && content) {
            header.addEventListener('click', () => {
                content.classList.toggle('d-none');
            });
        }
    });
});
