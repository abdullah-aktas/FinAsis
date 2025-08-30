// FinAsis - Küçük UX geliştirmeleri

document.addEventListener('DOMContentLoaded', function() {
  // Bootstrap alert'leri otomatik kapat
  var alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 4000);
  });

  // Tema geçişi
  var themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      document.body.classList.toggle('dark-theme');
      if(document.body.classList.contains('dark-theme')) {
        localStorage.setItem('finasis-theme', 'dark');
      } else {
        localStorage.setItem('finasis-theme', 'light');
      }
    });
  }
  // Sayfa yüklenince tema ayarla
  if(localStorage.getItem('finasis-theme') === 'dark') {
    document.body.classList.add('dark-theme');
  }

  // Bootstrap toast'ları otomatik başlat
  var toastElements = document.querySelectorAll('.toast');
  toastElements.forEach(function(toastEl) {
    var toast = new bootstrap.Toast(toastEl);
    toast.show();
  });
});

// Google Fonts yüklemesi (Inter, Open Sans, Fira Code)
(function() {
  var link = document.createElement('link');
  link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&family=Open+Sans:wght@400;600&family=Fira+Code&display=swap';
  link.rel = 'stylesheet';
  document.head.appendChild(link);
})();
// Bootstrap Icons yüklemesi
(function() {
  var link = document.createElement('link');
  link.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css';
  link.rel = 'stylesheet';
  document.head.appendChild(link);
})();
// Dark mode geçişi
function toggleTheme() {
  const theme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('finasis-theme', theme);
}
window.onload = function() {
  const saved = localStorage.getItem('finasis-theme');
  if (saved) document.body.setAttribute('data-theme', saved);
  // Hamburger menü
  const hamburger = document.querySelector('.hamburger');
  const navbar = document.querySelector('.navbar');
  if (hamburger && navbar) {
    hamburger.addEventListener('click', function() {
      navbar.classList.toggle('active');
    });
  }
};
// Swipe kartlar için (isteğe bağlı, touch event)
// (Ekstra swipe kütüphanesi gerekirse eklenebilir) 