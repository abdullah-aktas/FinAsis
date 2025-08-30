// Yüksek kontrast modu aç/kapa
function toggleContrast() {
  document.body.classList.toggle('a11y-contrast');
  localStorage.setItem('finasis-contrast', document.body.classList.contains('a11y-contrast') ? 'on' : 'off');
}
window.addEventListener('DOMContentLoaded', function() {
  if (localStorage.getItem('finasis-contrast') === 'on') {
    document.body.classList.add('a11y-contrast');
  }
  // Klavye ile gezilebilirlik için skip link
  const skip = document.createElement('a');
  skip.href = '#main-content';
  skip.className = 'sr-only';
  skip.innerText = 'Ana içeriğe atla';
  document.body.prepend(skip);
}); 