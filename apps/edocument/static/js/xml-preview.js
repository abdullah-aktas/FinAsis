document.addEventListener('DOMContentLoaded', function() {
    const xmlEditor = document.getElementById('xmlEditor');
    const lineNumbersToggle = document.getElementById('lineNumbersToggle');
    const wrapTextToggle = document.getElementById('wrapTextToggle');
    const formatBtn = document.getElementById('formatBtn');
    const validateBtn = document.getElementById('validateBtn');
    const signBtn = document.getElementById('signBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const xmlContent = document.getElementById('xmlContent');

    // Satır numaralarını göster/gizle
    function toggleLineNumbers() {
        xmlEditor.classList.toggle('with-line-numbers');
        if (xmlEditor.classList.contains('with-line-numbers')) {
            addLineNumbers();
        } else {
            removeLineNumbers();
        }
    }

    // Metin sarmayı göster/gizle
    function toggleWrapText() {
        xmlEditor.classList.toggle('wrap-text');
    }

    // Satır numaralarını ekle
    function addLineNumbers() {
        const lines = xmlEditor.value.split('\n');
        const lineNumbersDiv = document.createElement('div');
        lineNumbersDiv.className = 'line-numbers';
        
        lines.forEach((_, index) => {
            const lineNumber = document.createElement('div');
            lineNumber.textContent = index + 1;
            lineNumbersDiv.appendChild(lineNumber);
        });

        xmlEditor.parentElement.insertBefore(lineNumbersDiv, xmlEditor);
    }

    // Satır numaralarını kaldır
    function removeLineNumbers() {
        const lineNumbers = document.querySelector('.line-numbers');
        if (lineNumbers) {
            lineNumbers.remove();
        }
    }

    // XML'i formatla
    function formatXML() {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlEditor.value, 'text/xml');
            const serializer = new XMLSerializer();
            const formatted = serializer.serializeToString(xmlDoc)
                .replace(/></g, '>\n<')
                .replace(/\n/g, '\n    ')
                .replace(/    </g, '<');
            
            xmlEditor.value = formatted;
            if (xmlEditor.classList.contains('with-line-numbers')) {
                removeLineNumbers();
                addLineNumbers();
            }
        } catch (error) {
            alert('XML formatlanırken hata oluştu: ' + error.message);
        }
    }

    // XML'i doğrula
    function validateXML() {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlEditor.value, 'text/xml');
            
            if (xmlDoc.documentElement.nodeName === 'parsererror') {
                throw new Error('Geçersiz XML');
            }
            
            xmlEditor.classList.remove('error-line');
            xmlEditor.classList.add('valid-xml');
            alert('XML geçerli!');
        } catch (error) {
            xmlEditor.classList.remove('valid-xml');
            xmlEditor.classList.add('error-line');
            alert('XML doğrulama hatası: ' + error.message);
        }
    }

    // XML'i imzala
    function signXML() {
        // İmzalama işlemi için gerekli kodlar buraya eklenecek
        alert('XML imzalama özelliği henüz uygulanmadı.');
    }

    // XML'i indir
    function downloadXML() {
        const blob = new Blob([xmlEditor.value], { type: 'text/xml' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'document.xml';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // Event listeners
    lineNumbersToggle.addEventListener('change', toggleLineNumbers);
    wrapTextToggle.addEventListener('change', toggleWrapText);
    formatBtn.addEventListener('click', formatXML);
    validateBtn.addEventListener('click', validateXML);
    signBtn.addEventListener('click', signXML);
    downloadBtn.addEventListener('click', downloadXML);

    // Sayfa yüklendiğinde XML içeriğini editöre yükle
    if (xmlContent.value) {
        xmlEditor.value = xmlContent.value;
        if (lineNumbersToggle.checked) {
            toggleLineNumbers();
        }
    }
}); 