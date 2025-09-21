(function(){
  const state = {
    gold: 10000,
    goods: 0,
    reputation: 0,
    level: 1,
    experience: 0,
    quests: []
  };

  function el(id){ return document.getElementById(id); }

  function render(){
    if(el('gold')) el('gold').textContent = state.gold;
    if(el('goods')) el('goods').textContent = state.goods;
    if(el('reputation')) el('reputation').textContent = state.reputation;
    if(el('level')) el('level').textContent = state.level;
    if(el('experience')) el('experience').textContent = state.experience;

    const q = el('active-quests');
    if(q){
      q.innerHTML = state.quests.length ? '' : '<p class="text-muted">Görev yok</p>';
      state.quests.forEach(item => {
        const div = document.createElement('div');
        div.className = 'mb-2';
        div.innerHTML = `<strong>${item.title}</strong><br><small>${item.desc}</small>`;
        q.appendChild(div);
      });
    }
  }

  function init(){
    // Basit demo: başlangıç görevi
    state.quests.push({title:'İlk Ticaretini Yap', desc:'Bir şehir seç ve ticaret gerçekleştir.'});
    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
