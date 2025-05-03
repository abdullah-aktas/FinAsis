// Öğretmen Kontrol Paneli JavaScript

$(document).ready(function() {
    // Tooltip'leri etkinleştir
    $('[data-toggle="tooltip"]').tooltip();

    // İlerleme çubuklarını animasyonlu göster
    $('.progress-bar').each(function() {
        $(this).css('width', $(this).attr('aria-valuenow') + '%');
    });

    // Tablo sıralama
    $('.table').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Turkish.json"
        },
        "order": [[0, "desc"]],
        "pageLength": 10,
        "responsive": true
    });

    // Not verme formu doğrulama
    $('#gradeForm').on('submit', function(e) {
        var grade = $('#id_grade').val();
        if (grade < 0 || grade > 100) {
            e.preventDefault();
            alert('Not 0-100 arasında olmalıdır.');
        }
    });

    // Ödev durumu güncelleme
    $('.assignment-status').on('change', function() {
        var status = $(this).val();
        var assignmentId = $(this).data('assignment-id');
        
        $.ajax({
            url: '/teacher/update-assignment-status/',
            method: 'POST',
            data: {
                'assignment_id': assignmentId,
                'status': status,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Durum güncellenirken bir hata oluştu.');
                }
            }
        });
    });

    // Öğrenci ilerleme grafiği
    if ($('#studentProgressChart').length) {
        var ctx = document.getElementById('studentProgressChart').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: studentProgressData.labels,
                datasets: [{
                    label: 'Tamamlanma Yüzdesi',
                    data: studentProgressData.data,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#28a745'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Bildirim sistemi
    function checkNotifications() {
        $.ajax({
            url: '/teacher/check-notifications/',
            method: 'GET',
            success: function(response) {
                if (response.count > 0) {
                    $('#notificationBadge').text(response.count).show();
                    if (response.notifications.length > 0) {
                        var html = '';
                        response.notifications.forEach(function(notification) {
                            html += '<a class="dropdown-item" href="' + notification.url + '">';
                            html += notification.message;
                            html += '</a>';
                        });
                        $('#notificationList').html(html);
                    }
                } else {
                    $('#notificationBadge').hide();
                }
            }
        });
    }

    // Her 5 dakikada bir bildirimleri kontrol et
    setInterval(checkNotifications, 300000);
    checkNotifications();

    // Mobil menü
    $('#mobileMenuButton').on('click', function() {
        $('#sidebar').toggleClass('show');
    });

    // Sayfa yüklendiğinde mobil menüyü gizle
    if (window.innerWidth < 768) {
        $('#sidebar').removeClass('show');
    }
}); 