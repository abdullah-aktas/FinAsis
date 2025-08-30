if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(function(reg) {
        console.log('Service Worker registered!', reg);
      })
      .catch(function(err) {
        console.log('Service Worker registration failed: ', err);
      });
  });
} 