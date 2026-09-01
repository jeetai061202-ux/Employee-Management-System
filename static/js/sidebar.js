document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const toggleButton = document.getElementById("sidebarToggle");
    const overlay = document.getElementById("sidebarOverlay");

    if (!sidebar || !toggleButton) {
        return;
    }


    /*
    ==========================================
    Desktop Sidebar Toggle
    ==========================================
    */

    toggleButton.addEventListener("click", function () {

        if (window.innerWidth > 992) {

            document.body.classList.toggle("sidebar-collapsed");

        } else {

            sidebar.classList.toggle("mobile-open");

            if (overlay) {
                overlay.classList.toggle("show");
            }

        }

    });


    /*
    ==========================================
    Mobile Overlay
    ==========================================
    */

    if (overlay) {

        overlay.addEventListener("click", function () {

            sidebar.classList.remove("mobile-open");

            overlay.classList.remove("show");

        });

    }


    /*
    ==========================================
    Close Mobile Sidebar When Link Clicked
    ==========================================
    */

    const sidebarLinks =
        sidebar.querySelectorAll(".sidebar-menu a");


    sidebarLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            if (window.innerWidth <= 992) {

                sidebar.classList.remove("mobile-open");

                if (overlay) {
                    overlay.classList.remove("show");
                }

            }

        });

    });


    /*
    ==========================================
    Handle Window Resize
    ==========================================
    */

    window.addEventListener("resize", function () {

        if (window.innerWidth > 992) {

            sidebar.classList.remove("mobile-open");

            if (overlay) {
                overlay.classList.remove("show");
            }

        }

    });

});