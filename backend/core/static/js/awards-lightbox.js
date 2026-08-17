(function () {
    var awardsSliderEl = document.getElementById('awards-slider');
    var modalEl = document.getElementById('awardsGalleryModal');

    if (
        !awardsSliderEl ||
        !modalEl ||
        typeof Splide === 'undefined' ||
        typeof bootstrap === 'undefined'
    ) {
        return;
    }

    var openAtIndex = 0;
    var mainSplide = null;
    var thumbSplide = null;

    var slides = awardsSliderEl.querySelectorAll('.splide__slide');
    var totalSlides = slides.length;

    // =========================================================
    // ОСНОВНОЙ СЛАЙДЕР ПАТЕНТОВ
    // =========================================================

    var awardsSplide = new Splide(awardsSliderEl, {
        type: 'loop',
        drag: 'free',
        perPage: 4,
        gap: '1.25rem',
        padding: {
            left: '0',
            right: '0'
        },
        arrows: false,
        pagination: false,
        focus: 0,

        autoScroll: {
            speed: 0.25,
            pauseOnHover: false
        },

        breakpoints: {
            768: {
                perPage: 1.5
            }
        }
    });

    // Открываем модальное окно по клику
    awardsSplide.on('click', function (slide) {
        if (!slide || !slide.slide) {
            return;
        }

        var idx = slide.slide.getAttribute('data-slide-index');

        if (idx !== null) {
            openAtIndex = parseInt(idx, 10);

            if (isNaN(openAtIndex)) {
                openAtIndex = 0;
            }
        } else {
            openAtIndex = slide.index || 0;
        }

        if (totalSlides > 0) {
            openAtIndex = Math.max(
                0,
                Math.min(openAtIndex, totalSlides - 1)
            );
        }

        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    });

    // Подключаем AutoScroll только если расширение действительно загружено
    var extensions = {};

    if (typeof SplideAutoScroll !== 'undefined') {
        extensions.AutoScroll = SplideAutoScroll;
    }

    awardsSplide.mount(extensions);


    // =========================================================
    // MODAL
    // =========================================================

    modalEl.addEventListener('shown.bs.modal', function () {

        var mainEl = document.getElementById('top-slider-award');
        var thumbEl = document.getElementById('thumbnail-slider-award');

        if (!mainEl || !thumbEl) {
            console.error('[awards] Не найдены #top-slider-award или #thumbnail-slider-award');
            return;
        }

        // Проверяем структуру Splide
        var mainTrack = mainEl.querySelector('.splide__track');
        var mainList = mainEl.querySelector('.splide__list');

        var thumbTrack = thumbEl.querySelector('.splide__track');
        var thumbList = thumbEl.querySelector('.splide__list');

        if (!mainTrack || !mainList) {
            console.error('[awards] У #top-slider отсутствует .splide__track или .splide__list');
            return;
        }

        if (!thumbTrack || !thumbList) {
            console.error('[awards] У #thumbnail-slider отсутствует .splide__track или .splide__list');
            return;
        }

        // Если по какой-то причине экземпляры уже существуют,
        // сначала уничтожаем их
        if (mainSplide) {
            mainSplide.destroy();
            mainSplide = null;
        }

        if (thumbSplide) {
            thumbSplide.destroy();
            thumbSplide = null;
        }

        // =====================================================
        // Большой слайдер
        // =====================================================

        mainSplide = new Splide(mainEl, {
            type: 'fade',
            rewind: true,
            pagination: false,
            arrows: false,
            speed: 400
        });

        // =====================================================
        // Миниатюры
        // =====================================================

        thumbSplide = new Splide(thumbEl, {
            fixedWidth: 80,
            fixedHeight: 56,
            gap: 10,
            rewind: true,
            pagination: false,
            arrows: false,
            isNavigation: true,
            focus: 'center',

            breakpoints: {
                600: {
                    fixedWidth: 60,
                    fixedHeight: 44
                }
            }
        });

        // Связываем большой слайдер с миниатюрами
        mainSplide.sync(thumbSplide);

        mainSplide.mount();
        thumbSplide.mount();

        // Переходим к нужному патенту
        if (totalSlides > 0) {
            mainSplide.go(openAtIndex);
        }
    });


    // =========================================================
    // Закрытие modal
    // =========================================================

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


    // =========================================================
    // Клавиатура
    // =========================================================

    document.addEventListener('keydown', function (e) {

        if (!modalEl.classList.contains('show') || !mainSplide) {
            return;
        }

        if (e.key === 'ArrowLeft') {
            mainSplide.go('<');
            e.preventDefault();
        }

        if (e.key === 'ArrowRight') {
            mainSplide.go('>');
            e.preventDefault();
        }
    });

})();