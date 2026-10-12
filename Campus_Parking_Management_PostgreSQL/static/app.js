// Small UI enhancement: automatically hide alerts after a few seconds.
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e) {}
  });
}, 5000);
