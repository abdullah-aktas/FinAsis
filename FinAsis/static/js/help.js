const helpData = {
  genel: [
    {q: "Giriş yapamıyorum", a: "Şifrenizi unuttuysanız 'Şifremi Unuttum' bağlantısını kullanın. Hala sorun yaşıyorsanız destek ile iletişime geçin."},
    {q: "Dil/Tema nasıl değiştirilir?", a: "Sağ üstteki dil ve tema butonlarını kullanabilirsiniz."},
    {q: "Erişilebilirlik seçenekleri nerede?", a: "Sağ alttaki kontrast butonu ve klavye ile gezilebilirlik desteği mevcuttur."}
  ],
  admin: [
    {q: "Kullanıcı ekleme/silme", a: "Yönetici panelinden yeni kullanıcı ekleyebilir veya silebilirsiniz."},
    {q: "Şirket ayarları", a: "Ayarlar menüsünden şirket bilgilerini güncelleyebilirsiniz."},
    {q: "Veri yedekleme", a: "Raporlar veya dışa aktarım menüsünden verilerinizi yedekleyebilirsiniz."}
  ],
  muhasebeci: [
    {q: "Fatura oluşturma", a: "Faturalar menüsünden yeni fatura oluşturabilirsiniz."},
    {q: "Banka entegrasyonu", a: "Banka işlemleri menüsünden entegrasyonları yönetebilirsiniz."},
    {q: "Raporlama", a: "Raporlar sekmesinden gelir/gider ve bilanço raporlarına ulaşabilirsiniz."}
  ],
  calisan: [
    {q: "Bildirimler nerede?", a: "Sağ üstteki zil ikonundan bildirimlerinizi görebilirsiniz."},
    {q: "Eğitim modülleri", a: "Eğitim menüsünden size atanan eğitimleri görebilirsiniz."}
  ],
  ogrenci: [
    {q: "Oyun ve simülasyonlar", a: "Oyunlar menüsünden finansal simülasyonlara ulaşabilirsiniz."},
    {q: "Skorlarım nerede?", a: "Profilinizde skor ve başarımlarınızı görebilirsiniz."}
  ],
  ogretmen: [
    {q: "Ödev atama", a: "Eğitim modülünde öğrencilere ödev atayabilirsiniz."},
    {q: "Raporlar", a: "Sınıf ve öğrenci raporlarını eğitim panelinden görebilirsiniz."}
  ]
};
function renderHelp(role, search) {
  let items = helpData[role] || [];
  if (search) {
    items = items.filter(item => item.q.toLowerCase().includes(search.toLowerCase()) || item.a.toLowerCase().includes(search.toLowerCase()));
  }
  if (items.length === 0) {
    document.getElementById('helpContent').innerHTML = '<div class="alert alert-warning">Sonuç bulunamadı.</div>';
    return;
  }
  document.getElementById('helpContent').innerHTML = items.map(item => `<div class='mb-3'><strong>${item.q}</strong><br><span>${item.a}</span></div>`).join('');
}
document.addEventListener('DOMContentLoaded', function() {
  const roleSelect = document.getElementById('helpRoleSelect');
  const searchInput = document.getElementById('helpSearch');
  const helpModal = document.getElementById('helpModal');
  if (helpModal) {
    helpModal.addEventListener('show.bs.modal', function () {
      document.getElementById('helpContent').innerHTML = '<div class="alert alert-info">Hoş geldiniz! Size nasıl yardımcı olabilirim? Rolünüzü seçin veya arama kutusuna sorunuzu yazın.</div>';
    });
  }
  roleSelect.addEventListener('change', () => renderHelp(roleSelect.value, searchInput.value));
  searchInput.addEventListener('input', () => renderHelp(roleSelect.value, searchInput.value));
  renderHelp(roleSelect.value, '');
}); 