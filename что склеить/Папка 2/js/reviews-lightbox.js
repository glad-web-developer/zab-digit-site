(function () {
  var galleryEl = document.getElementById('reviewsFullscreenGallery');
  var imgEl = galleryEl ? galleryEl.querySelector('.reviews-fullscreen__img') : null;
  var closeBtn = galleryEl ? galleryEl.querySelector('.reviews-fullscreen__close') : null;
  var prevBtn = galleryEl ? galleryEl.querySelector('.reviews-fullscreen__prev') : null;
  var nextBtn = galleryEl ? galleryEl.querySelector('.reviews-fullscreen__next') : null;

  if (!galleryEl || !imgEl) return;

  var slides = [];
  document.querySelectorAll('.reviews__item').forEach(function (item) {
    var img = item.querySelector('img');
    if (img) slides.push({ src: img.src, alt: img.alt || '' });
  });

  var currentIndex = 0;
  var N = slides.length;

  function showSlide(index) {
    if (N === 0) return;
    currentIndex = (index + N) % N;
    imgEl.src = slides[currentIndex].src;
    imgEl.alt = slides[currentIndex].alt;
  }

  function openGallery(index) {
    if (N === 0) return;
    currentIndex = Math.max(0, Math.min(index, N - 1));
    showSlide(currentIndex);
    galleryEl.removeAttribute('hidden');
    galleryEl.setAttribute('aria-hidden', 'false');
    document.body.classList.add('reviews-fullscreen-open');
    closeBtn && closeBtn.focus();
  }

  function closeGallery() {
    galleryEl.setAttribute('hidden', '');
    galleryEl.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('reviews-fullscreen-open');
  }

  document.querySelectorAll('.reviews__item').forEach(function (el) {
    el.addEventListener('click', function () {
      var index = parseInt(el.getAttribute('data-slide-index'), 10);
      if (isNaN(index)) index = 0;
      openGallery(index);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', closeGallery);
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      showSlide(currentIndex - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      showSlide(currentIndex + 1);
    });
  }

  galleryEl.addEventListener('click', function (e) {
    if (e.target === galleryEl) closeGallery();
  });

  document.addEventListener('keydown', function (e) {
    if (galleryEl.hasAttribute('hidden')) return;
    if (e.key === 'Escape') {
      closeGallery();
      e.preventDefault();
    } else if (e.key === 'ArrowLeft') {
      showSlide(currentIndex - 1);
      e.preventDefault();
    } else if (e.key === 'ArrowRight') {
      showSlide(currentIndex + 1);
      e.preventDefault();
    }
  });
})();
