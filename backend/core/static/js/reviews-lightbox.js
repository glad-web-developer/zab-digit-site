(function () {
  var reviewsSliderEl = document.getElementById('reviews-slider');
  var modalEl = document.getElementById('reviewsGalleryModal');
  if (!reviewsSliderEl || !modalEl || typeof Splide === 'undefined' || typeof bootstrap === 'undefined') return;

  var openAtIndex = 0;
  var mainSplide = null;
  var thumbSplide = null;
  var totalSlides = reviewsSliderEl.querySelectorAll('.splide__slide').length;

    var reviewsSplide = new Splide('#reviews-slider', {
        type: 'loop',
        drag: 'free',
        perPage: 4,
        gap: '1.25rem',
        padding: {left: '0', right: '0'},
        arrows: false,
        pagination: false,
        focus: 0,
        autoScroll: {
            speed: 8.0,
            delay: 0,
            pauseOnHover: false,
            pauseOnFocus: false,
            waitForTransition: true
        },
        breakpoints: {
            768: {perPage: 1.5}
        }
    });

    reviewsSplide.on('click', function (slide) {
        var slideEl = slide.slide;
        var idx = slideEl.getAttribute('data-slide-index');
        if (idx !== null && idx !== undefined) {
            openAtIndex = parseInt(idx, 10);
            if (isNaN(openAtIndex)) openAtIndex = 0;
        } else {
            openAtIndex = slide.index;
        }
        openAtIndex = Math.max(0, Math.min(openAtIndex, totalSlides - 1));
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    });


    var extensions = {};
    var autoScrollLoaded = typeof SplideAutoScroll !== 'undefined';
    if (autoScrollLoaded) {
        extensions.AutoScroll = SplideAutoScroll;
    } else {
        console.warn('SplideAutoScroll not loaded – будет использован запасной скролл.');
    }

    reviewsSplide.mount(extensions);

    // ===== ЗАПУСК АВТОПРОКРУТКИ =====
    if (autoScrollLoaded) {
        // Если расширение загружено – используем его
        setTimeout(function () {
            reviewsSplide.play();
        }, 50);
    } else {
        // Запасной вариант: плавная прокрутка через setInterval
        var intervalId = setInterval(function () {
            reviewsSplide.go('+1');
        }, 1800); // каждые 2.5 сек
        // Останавливаем интервал, когда пользователь взаимодействует со слайдером
        reviewsSplide.on('drag', function () {
            clearInterval(intervalId);
        });
        // Можно перезапустить после окончания перетаскивания (опционально)
    }

    // ===== Модальное окно: инициализация слайдеров =====
    modalEl.addEventListener('shown.bs.modal', function () {
        var mainEl = document.getElementById('top-slider');
        var thumbEl = document.getElementById('thumbnail-slider');
        if (!mainEl || !thumbEl) return;

        mainSplide = new Splide('#top-slider', {
            type: 'fade',
            rewind: true,
            pagination: false,
            arrows: false
        });

        thumbSplide = new Splide('#thumbnail-slider', {
            fixedWidth: 80,
            fixedHeight: 56,
            gap: 10,
            rewind: true,
            pagination: false,
            isNavigation: true,
            focus: 'center',
            breakpoints: {
                600: {fixedWidth: 60, fixedHeight: 44}
            }
        });

        mainSplide.sync(thumbSplide);
        mainSplide.mount();
        thumbSplide.mount();
        mainSplide.go(openAtIndex);
    });

    modalEl.addEventListener('hidden.bs.modal', function () {
        if (mainSplide) {
            mainSplide.destroy();
            mainSplide = null;
        }
        if (thumbSplide) {
            thumbSplide.destroy();
            thumbSplide = null;
        }
    });

    // Клавиши ← → в модалке
    document.addEventListener('keydown', function (e) {
        if (!modalEl.classList.contains('show') || !mainSplide) return;
        if (e.key === 'ArrowLeft') {
            mainSplide.go('<');
            e.preventDefault();
        } else if (e.key === 'ArrowRight') {
            mainSplide.go('>');
            e.preventDefault();
        }
    });
})();