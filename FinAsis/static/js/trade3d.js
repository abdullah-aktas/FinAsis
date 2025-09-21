(function(){
  const api = {
    cities: '/games/trade-sim/cities/',
    products: '/games/trade-sim/products/',
    trade: '/games/trade-sim/city-trade/',
    cityMarket: '/games/trade-sim/city-market/'
  };

  function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  async function fetchJSON(url){
    const res = await fetch(url, {credentials:'same-origin'});
    if(!res.ok) throw new Error('HTTP '+res.status);
    return res.json();
  }

  async function loadCities(){
    try{
      const data = await fetchJSON(api.cities);
      const cities = data.cities || [];
      const fromSel = document.getElementById('fromCitySelect');
      const toSel = document.getElementById('toCitySelect');
      if(fromSel && toSel){
        fromSel.innerHTML = '';
        toSel.innerHTML = '';
        cities.forEach(c => {
          const o1 = document.createElement('option'); o1.value = c.id; o1.textContent = c.name; fromSel.appendChild(o1);
          const o2 = document.createElement('option'); o2.value = c.id; o2.textContent = c.name; toSel.appendChild(o2);
        });
        if(toSel.options.length>1) toSel.selectedIndex = 1;
      }
      return cities;
    }catch(e){ console.error('Şehirler alınamadı', e); return []; }
  }

  async function loadProducts(){
    try{
      const data = await fetchJSON(api.products);
      const products = data.products || [];
      const sel = document.getElementById('productSelect');
      if(sel){
        sel.innerHTML = '';
        products.forEach(p => { const o=document.createElement('option'); o.value=p.id; o.textContent=p.name; sel.appendChild(o); });
      }
      return products;
    }catch(e){ console.error('Ürünler alınamadı', e); return []; }
  }

  async function doTrade(){
    const fromSel = document.getElementById('fromCitySelect');
    const toSel = document.getElementById('toCitySelect');
    const prodSel = document.getElementById('productSelect');
    const amountEl = document.getElementById('amountInput');
    if(!(fromSel && toSel && prodSel && amountEl)) return;
    const payload = {
      from_city: parseInt(fromSel.value,10),
      to_city: parseInt(toSel.value,10),
      product_id: parseInt(prodSel.value,10),
      amount: parseInt(amountEl.value,10) || 1
    };
    try{
      const csrf = getCookie('csrftoken');
      const res = await fetch(api.trade, {
        method:'POST',
        headers:{'Content-Type':'application/json', 'X-CSRFToken': csrf || ''},
        body: JSON.stringify(payload),
        credentials:'same-origin'
      });
      const data = await res.json();
      if(res.ok){
        // Para güncellemesi (jenerik)
        const delta = (data.result && (data.result.profit || data.result.gain)) || data.profit || 0;
        const moneyEl = document.getElementById('money');
        if(moneyEl){
          const current = parseInt((moneyEl.textContent||'0').replace(/[^0-9-]/g,''), 10) || 0;
          moneyEl.textContent = current + (parseInt(delta,10)||0);
        }
        showToast('Ticaret başarılı!', 'success');
      } else {
        showToast('Hata: '+ (data.error || res.status), 'error');
      }
    }catch(e){ showToast('İstek hatası: '+ e.message, 'error'); }
  }

  // Basit toast bildirimi
  let toastContainer = null;
  function ensureToastContainer(){
    if(!toastContainer){
      toastContainer = document.createElement('div');
      toastContainer.style.position = 'fixed';
      toastContainer.style.right = '16px';
      toastContainer.style.bottom = '16px';
      toastContainer.style.zIndex = '9999';
      toastContainer.style.display = 'flex';
      toastContainer.style.flexDirection = 'column';
      toastContainer.style.gap = '8px';
      document.body.appendChild(toastContainer);
    }
  }
  function showToast(message, type){
    ensureToastContainer();
    const el = document.createElement('div');
    el.textContent = message;
    el.style.padding = '10px 14px';
    el.style.borderRadius = '8px';
    el.style.color = '#fff';
    el.style.fontSize = '14px';
    el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
    el.style.background = type === 'success' ? '#16a34a' : (type === 'warning' ? '#f59e0b' : '#ef4444');
    el.style.opacity = '0';
    el.style.transition = 'opacity .2s ease';
    toastContainer.appendChild(el);
    requestAnimationFrame(()=>{ el.style.opacity = '1'; });
    setTimeout(()=>{
      el.style.opacity = '0';
      setTimeout(()=>{ el.remove(); }, 220);
    }, 2800);
  }

  // Şehir pazar bilgisi (opsiyonel panel)
  async function fetchCityMarket(cityId){
    try{
      const url = cityId ? (api.cityMarket + '?city_id=' + encodeURIComponent(cityId)) : api.cityMarket;
      return await fetchJSON(url);
    }catch(e){
      console.warn('Pazar bilgisi alınamadı', e);
      return null;
    }
  }
  function updateMarketPanel(data){
    const panel = document.getElementById('marketPanel');
    if(!panel) return;
    if(!data){ panel.innerHTML = '<div class="text-muted">Pazar verisi yok</div>'; return; }
    // Esnek şablon: beklenen alanlar yoksa JSON göster
    if(Array.isArray(data) && data.length && (data[0].product || data[0].product_name)){
      const rows = data.map(it => {
        const name = it.product?.name || it.product_name || 'Ürün';
        const price = it.price ?? it.unit_price ?? it.cost ?? '-';
        const qty = it.quantity ?? it.supply ?? it.stock ?? '-';
        return `<div class="d-flex justify-content-between"><span>${name}</span><span>${price} | ${qty}</span></div>`;
      }).join('');
      panel.innerHTML = `<div class="small">${rows}</div>`;
    } else if(data && (data.items || data.markets)){
      const list = data.items || data.markets || [];
      const rows = list.map(it => {
        const name = it.product?.name || it.name || 'Ürün';
        const price = it.price ?? '-';
        return `<div class="d-flex justify-content-between"><span>${name}</span><span>${price}</span></div>`;
      }).join('');
      panel.innerHTML = `<div class="small">${rows}</div>`;
    } else {
      panel.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    }
  }

  function boot3D(cities){
    const container = document.getElementById('three-container');
    if(!container || !window.THREE){ return; }
    const {Scene, PerspectiveCamera, WebGLRenderer, SphereGeometry, MeshBasicMaterial, Mesh, Color, AmbientLight, Vector3} = THREE;

    const scene = new Scene();
    scene.background = new Color(0x000000);

    const camera = new PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
    const renderer = new WebGLRenderer({antialias:true});
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // OrbitControls
    let controls = null;
    if(THREE.OrbitControls){
      controls = new THREE.OrbitControls(camera, renderer.domElement);
    }

    const light = new AmbientLight(0xffffff, 0.9);
    scene.add(light);

    camera.position.set(0, 3, 8);
    if(controls){ controls.update(); }

    // Şehir küreleri ve etiketler
    const nodes = [];
    const labels = [];
    let selectedFromId = null;
    let selectedToId = null;
    let routeLine = null;
    const geo = new SphereGeometry(0.25, 24, 24);
    function makeLabelSprite(text){
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const fontSize = 48;
      ctx.font = `bold ${fontSize}px Arial`;
      const padding = 16;
      const metrics = ctx.measureText(text);
      const w = Math.ceil(metrics.width + padding*2);
      const h = Math.ceil(fontSize + padding*2);
      canvas.width = w; canvas.height = h;
      ctx.font = `bold ${fontSize}px Arial`;
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'center';
      // Arka plan yarı saydam
      ctx.fillStyle = 'rgba(0,0,0,0.45)';
      ctx.fillRect(0,0,w,h);
      // Konturlu yazı
      ctx.lineWidth = 8; ctx.strokeStyle = 'rgba(0,0,0,0.7)';
      ctx.strokeText(text, w/2, h/2+2);
      ctx.fillStyle = '#fff';
      ctx.fillText(text, w/2, h/2);
      const texture = new THREE.CanvasTexture(canvas);
      texture.minFilter = THREE.LinearFilter;
      const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
      const sprite = new THREE.Sprite(material);
      // Ölçek: dünya birimlerine göre ~1.8 genişlik
      const scaleX = 1.8;
      const scaleY = scaleX * (h/w);
      sprite.scale.set(scaleX, scaleY, 1);
      return sprite;
    }

    cities.forEach((c, idx) => {
      const mat = new MeshBasicMaterial({ color: 0x00ff99 });
      const mesh = new Mesh(geo, mat);
      // Varsayılan koordinatlar yoksa dairesel yerleşim
      const angle = (idx / Math.max(cities.length,1)) * Math.PI * 2;
      const r = 3.0;
      const x = (c.coordinates && c.coordinates.x) || Math.cos(angle) * r;
      const z = (c.coordinates && c.coordinates.y) || Math.sin(angle) * r;
      mesh.position.set(x, 0, z);
      mesh.userData = {id: c.id, name: c.name};
      scene.add(mesh);
      nodes.push(mesh);

      // Etiket
      const label = makeLabelSprite(c.name || 'Şehir');
      label.position.set(x, 0.6, z);
      label.userData.cityId = c.id;
      scene.add(label);
      labels.push(label);
    });

    function updateSelects(){
      const fromSel = document.getElementById('fromCitySelect');
      const toSel = document.getElementById('toCitySelect');
      if(fromSel && selectedFromId){ fromSel.value = String(selectedFromId); }
      if(toSel && selectedToId){ toSel.value = String(selectedToId); }
    }

    function clearRoute(){
      if(routeLine){ scene.remove(routeLine); routeLine.geometry.dispose(); routeLine.material.dispose(); routeLine = null; }
    }

    function drawRoute(){
      clearRoute();
      if(!selectedFromId || !selectedToId) return;
      const a = nodes.find(n=>n.userData.id===selectedFromId);
      const b = nodes.find(n=>n.userData.id===selectedToId);
      if(!(a&&b)) return;
      const pts = [a.position.clone(), b.position.clone()];
      const g = new THREE.BufferGeometry().setFromPoints(pts);
      const m = new THREE.LineBasicMaterial({ color: 0x00bcd4 });
      routeLine = new THREE.Line(g, m);
      scene.add(routeLine);
    }

    function setNodeVisual(node, selected){
      node.material.color.setHex(selected?0xffcc00:0x00ff99);
      node.scale.setScalar(selected?1.4:1.0);
    }

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    function onClick(event){
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = - ((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodes, false);
      if(intersects.length){
        const obj = intersects[0].object;
        const id = obj.userData.id;
        // Seçim mantığı: önce from, sonra to
        if(!selectedFromId || (selectedFromId && selectedToId)){
          // reset ve from ata
          nodes.forEach(n=>setNodeVisual(n, false));
          selectedFromId = id; selectedToId = null; setNodeVisual(obj, true); clearRoute();
          // Pazar panelini güncelle
          fetchCityMarket(selectedFromId).then(updateMarketPanel);
        } else if(selectedFromId && !selectedToId){
          if(id === selectedFromId){
            // aynı node'a tıklama: yok say
          } else {
            selectedToId = id; setNodeVisual(obj, true); drawRoute();
          }
        }
        updateSelects();
      }
    }
    renderer.domElement.addEventListener('click', onClick);

    // Dropdown senkronizasyonu
    function setSelectionFromDropdowns(){
      const fromSel = document.getElementById('fromCitySelect');
      const toSel = document.getElementById('toCitySelect');
      const fromId = fromSel && fromSel.value ? parseInt(fromSel.value,10) : null;
      const toId = toSel && toSel.value ? parseInt(toSel.value,10) : null;
      // Görselleri resetle
      nodes.forEach(n=>setNodeVisual(n, false));
      selectedFromId = fromId || null;
      selectedToId = toId || null;
      if(selectedFromId){
        const node = nodes.find(n=>n.userData.id===selectedFromId);
        if(node) setNodeVisual(node, true);
        fetchCityMarket(selectedFromId).then(updateMarketPanel);
      }
      if(selectedToId){
        const node = nodes.find(n=>n.userData.id===selectedToId);
        if(node) setNodeVisual(node, true);
      }
      drawRoute();
    }
    const fromSelEl = document.getElementById('fromCitySelect');
    const toSelEl = document.getElementById('toCitySelect');
    if(fromSelEl){ fromSelEl.addEventListener('change', setSelectionFromDropdowns); }
    if(toSelEl){ toSelEl.addEventListener('change', setSelectionFromDropdowns); }

    function onResize(){
      const w = container.clientWidth;
      const h = container.clientHeight;
      renderer.setSize(w, h);
      camera.aspect = w/h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);

    function animate(){
      requestAnimationFrame(animate);
      if(controls){ controls.update(); }
      renderer.render(scene, camera);
    }
    animate();
  }

  async function init(){
    const cities = await loadCities();
    await loadProducts();
    const tradeBtn = document.getElementById('doTradeBtn');
    if(tradeBtn){ tradeBtn.addEventListener('click', doTrade); }
    boot3D(cities);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
