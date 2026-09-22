document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const toggleButton = document.getElementById("sidebarToggle");
    const overlay = document.getElementById("sidebarOverlay");
    const resizeHandle = document.getElementById("sidebarResizeHandle");

    const SIDEBAR_STORAGE_KEY = "hrms_sidebar_collapsed";
    const SIDEBAR_WIDTH_KEY = "hrms_sidebar_width";

    const DEFAULT_WIDTH = 270;
    const MIN_WIDTH = 200;
    const MAX_WIDTH = 400;


    /*
    ==========================================
    Sidebar Width Helpers
    ==========================================
    */

    function getSavedSidebarWidth() {

        const savedWidth =
            localStorage.getItem(SIDEBAR_WIDTH_KEY);

        if (!savedWidth) {

            return DEFAULT_WIDTH;

        }

        const width = parseInt(
            savedWidth,
            10
        );

        if (
            isNaN(width) ||
            width < MIN_WIDTH ||
            width > MAX_WIDTH
        ) {

            return DEFAULT_WIDTH;

        }

        return width;

    }


    function setSidebarWidth(width) {

        width = Math.round(width);

        if (width < MIN_WIDTH) {

            width = MIN_WIDTH;

        }

        if (width > MAX_WIDTH) {

            width = MAX_WIDTH;

        }

        document.documentElement.style.setProperty(
            "--sidebar-width",
            width + "px"
        );

        return width;

    }


    function saveSidebarWidth(width) {

        localStorage.setItem(
            SIDEBAR_WIDTH_KEY,
            String(width)
        );

    }


    /*
    ==========================================
    Resize Handle Position
    ==========================================
    */

    function updateResizeHandlePosition() {

        if (!resizeHandle) {

            return;

        }

        if (window.innerWidth <= 992) {

            resizeHandle.style.left = "";

            return;

        }

        if (
            document.body.classList.contains(
                "sidebar-collapsed"
            )
        ) {

            resizeHandle.style.left = "";

            return;

        }

        const sidebarWidth =
            getCurrentSidebarWidth();

        resizeHandle.style.left =
            sidebarWidth + "px";

    }


    function getCurrentSidebarWidth() {

        const rootStyles =
            getComputedStyle(
                document.documentElement
            );

        const cssWidth =
            rootStyles.getPropertyValue(
                "--sidebar-width"
            ).trim();

        const width =
            parseInt(cssWidth, 10);

        if (
            isNaN(width) ||
            width < MIN_WIDTH ||
            width > MAX_WIDTH
        ) {

            return DEFAULT_WIDTH;

        }

        return width;

    }


    /*
    ==========================================
    Restore Desktop Sidebar State
    ==========================================
    */

    function restoreDesktopSidebarState() {

        if (window.innerWidth <= 992) {

            return;

        }

        const savedWidth =
            getSavedSidebarWidth();

        setSidebarWidth(savedWidth);


        const isCollapsed =
            localStorage.getItem(
                SIDEBAR_STORAGE_KEY
            ) === "true";


        document.body.classList.toggle(
            "sidebar-collapsed",
            isCollapsed
        );


        document.documentElement.classList.remove(
            "sidebar-collapsed-preload"
        );


        document.documentElement.classList.remove(
            "sidebar-width-preload"
        );


        updateResizeHandlePosition();

    }


    /*
    ==========================================
    Sidebar Toggle
    ==========================================
    */

    if (toggleButton) {

        toggleButton.addEventListener(
            "click",
            function () {


                /*
                ------------------------------------------
                Desktop
                ------------------------------------------
                */

                if (window.innerWidth > 992) {

                    const isCollapsed =
                        !document.body.classList.contains(
                            "sidebar-collapsed"
                        );


                    document.body.classList.toggle(
                        "sidebar-collapsed",
                        isCollapsed
                    );


                    localStorage.setItem(
                        SIDEBAR_STORAGE_KEY,
                        isCollapsed
                            ? "true"
                            : "false"
                    );


                    /*
                    ------------------------------------------
                    When Expanding
                    ------------------------------------------

                    The previously saved custom width
                    remains unchanged.
                    */

                    if (!isCollapsed) {

                        const savedWidth =
                            getSavedSidebarWidth();

                        setSidebarWidth(
                            savedWidth
                        );

                    }


                    updateResizeHandlePosition();


                    return;

                }


                /*
                ------------------------------------------
                Mobile / Tablet
                ------------------------------------------
                */

                sidebar.classList.toggle(
                    "mobile-open"
                );


                if (overlay) {

                    overlay.classList.toggle(
                        "show"
                    );

                }

            }
        );

    }


    /*
    ==========================================
    Mobile Overlay
    ==========================================
    */

    if (overlay) {

        overlay.addEventListener(
            "click",
            function () {

                sidebar.classList.remove(
                    "mobile-open"
                );

                overlay.classList.remove(
                    "show"
                );

            }
        );

    }


    /*
    ==========================================
    Sidebar Links
    ==========================================
    */

    if (sidebar) {

        const sidebarLinks =
            sidebar.querySelectorAll(
                ".sidebar-menu a"
            );


        sidebarLinks.forEach(function (link) {

            link.addEventListener(
                "click",
                function () {


                    /*
                    ------------------------------------------
                    Mobile / Tablet
                    ------------------------------------------
                    */

                    if (window.innerWidth <= 992) {

                        sidebar.classList.remove(
                            "mobile-open"
                        );


                        if (overlay) {

                            overlay.classList.remove(
                                "show"
                            );

                        }

                    }


                    /*
                    ------------------------------------------
                    Desktop
                    ------------------------------------------

                    IMPORTANT:

                    Do NOT modify:

                    - sidebar-collapsed
                    - sidebar width
                    - localStorage state

                    Navigation must preserve both
                    sidebar state and sidebar width.
                    */

                }
            );

        });

    }


    /*
    ==========================================
    Sidebar Resize
    ==========================================
    */

    let isResizing = false;
    let resizeStartX = 0;
    let resizeStartWidth = DEFAULT_WIDTH;


    if (resizeHandle) {

        resizeHandle.addEventListener(
            "pointerdown",
            function (event) {

                /*
                ------------------------------------------
                Desktop Only
                ------------------------------------------
                */

                if (window.innerWidth <= 992) {

                    return;

                }


                /*
                ------------------------------------------
                Do Not Resize While Collapsed
                ------------------------------------------
                */

                if (
                    document.body.classList.contains(
                        "sidebar-collapsed"
                    )
                ) {

                    return;

                }


                isResizing = true;

                resizeStartX = event.clientX;

                resizeStartWidth =
                    getCurrentSidebarWidth();


                document.body.classList.add(
                    "sidebar-resizing"
                );


                resizeHandle.setPointerCapture(
                    event.pointerId
                );


                event.preventDefault();

            }
        );


        resizeHandle.addEventListener(
            "pointermove",
            function (event) {

                if (!isResizing) {

                    return;

                }


                if (window.innerWidth <= 992) {

                    return;

                }


                const difference =
                    event.clientX - resizeStartX;


                let newWidth =
                    resizeStartWidth + difference;


                /*
                ------------------------------------------
                Apply Minimum / Maximum Limits
                ------------------------------------------
                */

                if (newWidth < MIN_WIDTH) {

                    newWidth = MIN_WIDTH;

                }


                if (newWidth > MAX_WIDTH) {

                    newWidth = MAX_WIDTH;

                }


                newWidth =
                    setSidebarWidth(
                        newWidth
                    );


                /*
                ------------------------------------------
                Update Handle Position
                ------------------------------------------
                */

                resizeHandle.style.left =
                    newWidth + "px";


                event.preventDefault();

            }
        );


        function stopSidebarResize(event) {

            if (!isResizing) {

                return;

            }


            isResizing = false;


            const finalWidth =
                getCurrentSidebarWidth();


            saveSidebarWidth(
                finalWidth
            );


            document.body.classList.remove(
                "sidebar-resizing"
            );


            if (
                event &&
                resizeHandle.hasPointerCapture &&
                resizeHandle.hasPointerCapture(
                    event.pointerId
                )
            ) {

                resizeHandle.releasePointerCapture(
                    event.pointerId
                );

            }


            updateResizeHandlePosition();

        }


        resizeHandle.addEventListener(
            "pointerup",
            stopSidebarResize
        );


        resizeHandle.addEventListener(
            "pointercancel",
            stopSidebarResize
        );


        resizeHandle.addEventListener(
            "lostpointercapture",
            function () {

                if (isResizing) {

                    const finalWidth =
                        getCurrentSidebarWidth();


                    saveSidebarWidth(
                        finalWidth
                    );


                    isResizing = false;


                    document.body.classList.remove(
                        "sidebar-resizing"
                    );


                    updateResizeHandlePosition();

                }

            }
        );

    }


    /*
    ==========================================
    Window Resize
    ==========================================
    */

    window.addEventListener(
        "resize",
        function () {


            /*
            ------------------------------------------
            Desktop
            ------------------------------------------
            */

            if (window.innerWidth > 992) {

                sidebar.classList.remove(
                    "mobile-open"
                );


                if (overlay) {

                    overlay.classList.remove(
                        "show"
                    );

                }


                restoreDesktopSidebarState();

            }


            /*
            ------------------------------------------
            Mobile / Tablet
            ------------------------------------------
            */

            else {

                document.body.classList.remove(
                    "sidebar-collapsed"
                );


                document.body.classList.remove(
                    "sidebar-resizing"
                );


                document.documentElement.classList.remove(
                    "sidebar-collapsed-preload"
                );


                document.documentElement.classList.remove(
                    "sidebar-width-preload"
                );


                if (resizeHandle) {

                    resizeHandle.style.left = "";

                }


                isResizing = false;

            }

        }
    );


    /*
    ==========================================
    Initial State
    ==========================================
    */

    restoreDesktopSidebarState();

});