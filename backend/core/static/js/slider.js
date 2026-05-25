(function() {
    const carousel = document.querySelector('.carousel');
    const track = carousel.querySelector('.carousel-track');

    function moveCarousel() {
        const slideWidth = track.children[0].clientWidth;
        const gap = 16;
        const itemWidth = slideWidth + gap;
        let currentPos = 0;

        currentPos -= itemWidth;
        track.style.transform = `translateX(${currentPos}px)`;
        
        // После завершения анимации переносим первый элемент в конец
        setTimeout(() => {
        const firstSlide = track.querySelector('.slide');
        track.appendChild(firstSlide);
        currentPos += itemWidth;
        track.style.transition = 'none';
        track.style.transform = `translateX(${currentPos}px)`;
        
        // Восстанавливаем переход для следующей анимации
        setTimeout(() => {
            track.style.transition = 'transform 0.5s ease';
            moveCarousel();
        }, 20);
        }, 1200);
    }

    // Запускаем карусель
    moveCarousel();
})();