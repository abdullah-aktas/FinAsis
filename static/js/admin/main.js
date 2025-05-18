/**
 * FinAsis Admin Panel Ana JavaScript Dosyası
 */

// DOM yüklendikten sonra çalışacak kodlar
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle Fonksiyonu
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    const adminContent = document.querySelector('.admin-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            adminSidebar.classList.toggle('collapsed');
            adminContent.classList.toggle('expanded');
            
            // Kullanıcı tercihini localStorage'a kaydet
            const isCollapsed = adminSidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Sayfa yüklendiğinde kullanıcı tercihini hatırla
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            adminSidebar.classList.add('collapsed');
            adminContent.classList.add('expanded');
        }
    }
    
    // Tooltips Aktivasyonu
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Tarih Filtreleme
    const dateRangeSelector = document.getElementById('dateRangeSelector');
    if (dateRangeSelector) {
        dateRangeSelector.addEventListener('change', function() {
            const value = this.value;
            let startDate = null;
            let endDate = new Date();
            
            const today = new Date();
            
            switch(value) {
                case 'today':
                    startDate = today;
                    break;
                case 'yesterday':
                    startDate = new Date(today);
                    startDate.setDate(today.getDate() - 1);
                    endDate = new Date(today);
                    endDate.setDate(today.getDate() - 1);
                    break;
                case 'last7days':
                    startDate = new Date(today);
                    startDate.setDate(today.getDate() - 6);
                    break;
                case 'last30days':
                    startDate = new Date(today);
                    startDate.setDate(today.getDate() - 29);
                    break;
                case 'thisMonth':
                    startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                    break;
                case 'lastMonth':
                    startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                    endDate = new Date(today.getFullYear(), today.getMonth(), 0);
                    break;
                case 'custom':
                    document.getElementById('customDateRange').style.display = 'flex';
                    return;
                default:
                    startDate = new Date(today);
                    startDate.setDate(today.getDate() - 6);
            }
            
            if (startDate && endDate) {
                document.getElementById('startDate').value = formatDate(startDate);
                document.getElementById('endDate').value = formatDate(endDate);
                
                // Tarih değiştiğinde filtreleme yapabilirsiniz
                filterByDateRange(startDate, endDate);
            }
            
            document.getElementById('customDateRange').style.display = 'none';
        });
    }
    
    // Özel tarih aralığında filtreleme
    const applyDateFilter = document.getElementById('applyDateFilter');
    if (applyDateFilter) {
        applyDateFilter.addEventListener('click', function() {
            const startDate = new Date(document.getElementById('startDate').value);
            const endDate = new Date(document.getElementById('endDate').value);
            
            if (startDate && endDate) {
                filterByDateRange(startDate, endDate);
            }
        });
    }
    
    // Tablo Arama Fonksiyonu
    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.querySelector('.admin-table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    }
    
    // Tüm Bildirimleri Okundu İşaretle
    const markAllRead = document.querySelector('.mark-all-read');
    if (markAllRead) {
        markAllRead.addEventListener('click', function(e) {
            e.preventDefault();
            
            const unreadNotifications = document.querySelectorAll('.notification-item.unread');
            unreadNotifications.forEach(item => {
                item.classList.remove('unread');
            });
            
            const notificationCount = document.querySelector('.notification-count');
            if (notificationCount) {
                notificationCount.textContent = '0';
                notificationCount.style.display = 'none';
            }
            
            // AJAX ile sunucuya bildirileri okundu olarak işaretleme isteği gönderilir
            // Bu sadece UI için bir önizlemedir
            
            // Bildirim sayısını sıfırla
            const badgeCount = document.querySelector('.notification-btn .badge');
            if (badgeCount) {
                badgeCount.textContent = '0';
                badgeCount.style.display = 'none';
            }
        });
    }
    
    // Form Doğrulama
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Dosya Yükleme Önizlemesi
    const fileInput = document.querySelector('.custom-file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = document.querySelector('.custom-file-label');
            label.textContent = fileName || 'Dosya Seçin...';
            
            // Resim önizlemesi
            if (this.files[0] && this.files[0].type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.img-preview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Tablo ile satır seçme
    const tableCheckAll = document.querySelector('.check-all');
    if (tableCheckAll) {
        tableCheckAll.addEventListener('change', function() {
            const isChecked = this.checked;
            const checkboxes = document.querySelectorAll('.row-checkbox');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                const row = checkbox.closest('tr');
                if (row) {
                    if (isChecked) {
                        row.classList.add('selected');
                    } else {
                        row.classList.remove('selected');
                    }
                }
            });
            
            updateSelectedCount();
        });
        
        // Satır seçildiğinde satırın görünümünü güncelle
        const rowCheckboxes = document.querySelectorAll('.row-checkbox');
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const row = this.closest('tr');
                if (row) {
                    if (this.checked) {
                        row.classList.add('selected');
                    } else {
                        row.classList.remove('selected');
                    }
                }
                
                updateSelectedCount();
                
                // Tüm satırlar seçildiyse "Tümünü Seç" kutusunu da işaretle
                const allCheckboxes = document.querySelectorAll('.row-checkbox');
                const checkedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
                if (tableCheckAll) {
                    tableCheckAll.checked = allCheckboxes.length === checkedCheckboxes.length;
                }
            });
        });
    }
    
    // Koşullu Form Alanları
    const conditionalSelects = document.querySelectorAll('.conditional-select');
    conditionalSelects.forEach(select => {
        select.addEventListener('change', function() {
            const targetId = this.dataset.target;
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const showValue = this.dataset.showValue;
                if (this.value === showValue) {
                    targetElement.style.display = 'block';
                } else {
                    targetElement.style.display = 'none';
                }
            }
        });
        
        // Sayfa yüklendiğinde durumu güncelle
        select.dispatchEvent(new Event('change'));
    });
    
    // Varsayılan olarak açık paneller
    initializePanels();
});

// Yardımcı Fonksiyonlar

// Tarih formatını YYYY-MM-DD olarak biçimlendirir
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Tarih aralığına göre filtreleme yapar
function filterByDateRange(startDate, endDate) {
    // Bu fonksiyon, tarih aralığına göre verileri filtrelemek için kullanılabilir
    // Örnek implementasyon:
    console.log(`Filtering data from ${startDate.toISOString()} to ${endDate.toISOString()}`);
    
    // AJAX ile filtreleme yapabilir veya sayfayı yeniden yükleyebilirsiniz
    // Burada sadece konsola yazdırılmıştır
}

// Seçili satır sayısını günceller
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.row-checkbox:checked').length;
    const countElement = document.querySelector('.selected-count');
    
    if (countElement) {
        countElement.textContent = selectedCount;
        
        const actionsBar = document.querySelector('.batch-actions');
        if (actionsBar) {
            if (selectedCount > 0) {
                actionsBar.classList.add('show');
            } else {
                actionsBar.classList.remove('show');
            }
        }
    }
}

// Panel durumlarını başlat
function initializePanels() {
    const panels = document.querySelectorAll('.collapsible-panel');
    panels.forEach(panel => {
        const panelId = panel.getAttribute('id');
        const isOpen = localStorage.getItem(`panel_${panelId}`) !== 'closed';
        
        const collapseElement = bootstrap.Collapse.getInstance(panel);
        
        if (isOpen) {
            if (!collapseElement) {
                new bootstrap.Collapse(panel, { show: true });
            } else {
                collapseElement.show();
            }
        } else {
            if (!collapseElement) {
                new bootstrap.Collapse(panel, { show: false });
            } else {
                collapseElement.hide();
            }
        }
        
        panel.addEventListener('shown.bs.collapse', function() {
            localStorage.setItem(`panel_${panelId}`, 'open');
        });
        
        panel.addEventListener('hidden.bs.collapse', function() {
            localStorage.setItem(`panel_${panelId}`, 'closed');
        });
    });
}

// Grafik renkleri
const chartColors = {
    primary: '#0097a7',
    secondary: '#718096',
    success: '#38A169',
    warning: '#ED8936',
    danger: '#E53E3E',
    info: '#3182CE',
    light: '#EDF2F7',
    dark: '#1A202C'
}; 