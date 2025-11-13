(function(){
  const btn=document.getElementById('darkModeToggle');
  if(!btn) return;
  const root=document.body;
  function setTheme(t){root.setAttribute('data-theme',t);localStorage.setItem('theme',t);btn.innerHTML=t==='dark'?'<i class="bi bi-brightness-high-fill"></i>':'<i class="bi bi-moon-fill"></i>'}
  document.addEventListener('DOMContentLoaded',()=>{setTheme(localStorage.getItem('theme')||'light');});
  btn.addEventListener('click',()=>{setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark');});
})();