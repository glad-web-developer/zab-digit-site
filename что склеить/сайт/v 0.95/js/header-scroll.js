(function () {
  var header = document.querySelector('.header');
  if (!header) return;

  var scrollThreshold = 20;

  function updateHeader() {
    if (window.scrollY > scrollThreshold) {
      header.classList.add('header--scrolled');
    } else {
      header.classList.remove('header--scrolled');
    }
  }

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
})();
