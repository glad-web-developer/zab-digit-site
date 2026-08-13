(function () {
    var header = document.querySelector('.header');
    if (!header) return;

    // Состояние шапки
    function updateHeader() {
        header.classList.toggle(
            'header--scrolled',
            window.scrollY > 20
        );
    }

    // Активный пункт меню
    function updateActiveLink() {
        var links = document.querySelectorAll('.menu-link');
        var currentPath = window.location.pathname;
        var currentHash = decodeURIComponent(
            window.location.hash.substring(1)
        );

        links.forEach(function (link) {
            var href = link.getAttribute('href') || '';

            // Убираем активность
            link.classList.remove('menu-link-active');

            // КЕЙСЫ
            if (currentPath === '/project/' && href === '/project/') {
                link.classList.add('menu-link-active');
                return;
            }

            // ЯКОРЯ
            if (
                currentHash &&
                href.endsWith('#' + currentHash)
            ) {
                link.classList.add('menu-link-active');
            }
        });
    }

    updateHeader();
    updateActiveLink();

    window.addEventListener('scroll', updateHeader, {
        passive: true
    });

    window.addEventListener('hashchange', updateActiveLink);

})();