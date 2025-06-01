function fetchHelp(role, search) {
  let url = `/yonetim/api/help-content/?role=${role}`;
  fetch(url)
    .then(resp => resp.json())
    .then(data => {
      let items = data.items || [];
      if (search) {
        items = items.filter(item => item.title.toLowerCase().includes(search.toLowerCase()) || item.content.toLowerCase().includes(search.toLowerCase()));
      }
      if (items.length === 0) {
        document.getElementById('helpContent').innerHTML = '<div class="alert alert-warning">Sonuç bulunamadı.</div>';
        return;
      }
      document.getElementById('helpContent').innerHTML = items.map(item => `<div class='mb-3'><strong>${item.title}</strong><br><span>${item.content}</span><br><small class='text-muted'>Güncellendi: ${item.updated_at}</small></div>`).join('');
    });
}
document.addEventListener('DOMContentLoaded', function() {
  const roleSelect = document.getElementById('helpRoleSelect');
  const searchInput = document.getElementById('helpSearch');
  const helpModal = document.getElementById('helpModal');
  if (helpModal) {
    helpModal.addEventListener('show.bs.modal', function () {
      document.getElementById('helpContent').innerHTML = '<div class="alert alert-info">Hoş geldiniz! Size nasıl yardımcı olabilirim? Rolünüzü seçin veya arama kutusuna sorunuzu yazın.</div>';
      fetchHelp(roleSelect.value, searchInput.value);
    });
  }
  roleSelect.addEventListener('change', () => fetchHelp(roleSelect.value, searchInput.value));
  searchInput.addEventListener('input', () => fetchHelp(roleSelect.value, searchInput.value));
  fetchHelp(roleSelect.value, '');
}); 