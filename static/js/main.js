document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* =====================================================
           PUBLIC ARTICLES + URDU ADAB — READ MORE / READ LESS
           Single page. Only the clicked card expands.
           ===================================================== */

        const expandableToggles =
            document.querySelectorAll(
                "[data-article-toggle], [data-adab-toggle]"
            );

        function setExpandableHeight(content, open) {

            if (!content) {
                return;
            }

            if (open) {

                content.style.maxHeight = "0px";

                requestAnimationFrame(() => {
                    content.style.maxHeight =
                        content.scrollHeight + "px";
                });

            } else {

                content.style.maxHeight =
                    content.scrollHeight + "px";

                requestAnimationFrame(() => {
                    content.style.maxHeight = "0px";
                });
            }
        }

        expandableToggles.forEach((button) => {

            button.addEventListener("click", () => {

                const card =
                    button.closest(
                        "[data-article-card], [data-adab-card]"
                    );

                if (!card) {
                    return;
                }

                const content =
                    card.querySelector(
                        "[data-article-content], [data-adab-content]"
                    );

                const text =
                    button.querySelector(
                        ".read-more-text"
                    );

                const expanded =
                    !card.classList.contains(
                        "is-expanded"
                    );

                card.classList.toggle(
                    "is-expanded",
                    expanded
                );

                button.setAttribute(
                    "aria-expanded",
                    expanded ? "true" : "false"
                );

                if (content) {

                    content.setAttribute(
                        "aria-hidden",
                        expanded ? "false" : "true"
                    );

                    setExpandableHeight(
                        content,
                        expanded
                    );
                }

                if (text) {
                    text.textContent =
                        expanded
                            ? "Read Less"
                            : "Read More";
                }
            });
        });

        /* Keep an already-open article/adab item correct if the viewport changes. */
        window.addEventListener("resize", () => {

            document
                .querySelectorAll(
                    "[data-article-card].is-expanded [data-article-content], " +
                    "[data-adab-card].is-expanded [data-adab-content]"
                )
                .forEach((content) => {
                    content.style.maxHeight =
                        content.scrollHeight + "px";
                });
        });

        /* =====================================================
           PUBLIC MOBILE MENU
        ===================================================== */

        const publicToggle =
            document.getElementById(
                "menuBtn"
            );

        const publicNav =
            document.getElementById(
                "navLinks"
            );


        function closePublicMenu() {

            if (!publicNav) {
                return;
            }

            publicNav.classList.remove(
                "show"
            );

            if (publicToggle) {

                publicToggle.innerHTML =
                    '<i class="fa-solid fa-bars"></i>';

                publicToggle.classList.remove("active");

                publicToggle.setAttribute(
                    "aria-label",
                    "Open navigation menu"
                );

                publicToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        }


        function openPublicMenu() {

            if (!publicNav) {
                return;
            }

            publicNav.classList.add(
                "show"
            );

            if (publicToggle) {

                publicToggle.innerHTML =
                    '<i class="fa-solid fa-xmark"></i>';

                publicToggle.classList.add("active");

                publicToggle.setAttribute(
                    "aria-label",
                    "Close navigation menu"
                );

                publicToggle.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        }


        if (
            publicToggle &&
            publicNav
        ) {

            publicToggle.setAttribute(
                "aria-expanded",
                "false"
            );


            publicToggle.setAttribute(
                "aria-controls",
                "navLinks"
            );


            publicToggle.addEventListener(
                "click",
                () => {

                    const isOpen =
                        publicNav.classList.contains(
                            "open"
                        );


                    if (isOpen) {

                        closePublicMenu();

                    } else {

                        openPublicMenu();

                    }

                }
            );


            publicNav
                .querySelectorAll("a")
                .forEach(
                    (link) => {

                        link.addEventListener(
                            "click",
                            closePublicMenu
                        );

                    }
                );


            window.addEventListener(
                "resize",
                () => {

                    if (
                        window.innerWidth > 780
                    ) {

                        closePublicMenu();

                    }

                }
            );

        }


        /* =====================================================
           ADMIN MOBILE SIDEBAR
        ===================================================== */

        const sidebarToggle =
            document.getElementById(
                "sidebarToggle"
            );

        const sidebar =
            document.getElementById(
                "adminSidebar"
            );

        const sidebarClose =
            document.getElementById(
                "sidebarClose"
            );

        const adminOverlay =
            document.getElementById(
                "adminOverlay"
            );


        function openAdminSidebar() {

            if (!sidebar) {
                return;
            }

            sidebar.classList.add(
                "open"
            );


            if (adminOverlay) {

                adminOverlay.classList.add(
                    "show"
                );

            }


            document.body.classList.add(
                "menu-open"
            );

        }


        function closeAdminSidebar() {

            if (!sidebar) {
                return;
            }

            sidebar.classList.remove(
                "open"
            );


            if (adminOverlay) {

                adminOverlay.classList.remove(
                    "show"
                );

            }


            document.body.classList.remove(
                "menu-open"
            );

        }


        if (sidebarToggle) {

            sidebarToggle.addEventListener(
                "click",
                openAdminSidebar
            );

        }


        if (sidebarClose) {

            sidebarClose.addEventListener(
                "click",
                closeAdminSidebar
            );

        }


        if (adminOverlay) {

            adminOverlay.addEventListener(
                "click",
                closeAdminSidebar
            );

        }


        if (sidebar) {

            sidebar
                .querySelectorAll("a")
                .forEach(
                    (link) => {

                        link.addEventListener(
                            "click",
                            () => {

                                if (
                                    window.innerWidth <= 900
                                ) {

                                    closeAdminSidebar();

                                }

                            }
                        );

                    }
                );

        }


        window.addEventListener(
            "resize",
            () => {

                if (
                    window.innerWidth > 900
                ) {

                    closeAdminSidebar();

                }

            }
        );


        /* =====================================================
           BACK TO TOP
        ===================================================== */

        const backTop =
            document.getElementById(
                "backTop"
            );


        if (backTop) {

            const updateBackTop =
                () => {

                    backTop.classList.toggle(
                        "show",
                        window.scrollY > 350
                    );

                };


            window.addEventListener(
                "scroll",
                updateBackTop,
                {
                    passive: true
                }
            );


            updateBackTop();


            backTop.addEventListener(
                "click",
                () => {

                    window.scrollTo({
                        top: 0,
                        behavior: "smooth"
                    });

                }
            );

        }


        /* =====================================================
           BAYAN FORM
        ===================================================== */

        const bayanForm =
            document.getElementById(
                "bayanForm"
            );


        if (bayanForm) {

            initBayanForm(
                bayanForm
            );

        }


        /* =====================================================
           BOOK ORDER FORM
        ===================================================== */

        const bookOrderForm =
            document.getElementById(
                "bookOrderForm"
            );


        if (bookOrderForm) {

            initBookOrderForm(
                bookOrderForm
            );

        }

    }
);


/* =========================================================
   BAYAN FORM INITIALIZER
========================================================= */

function initBayanForm(
    bayanForm
) {

    const typeOptions =
        bayanForm.querySelectorAll(
            ".type-option"
        );


    const onlineMode =
        document.getElementById(
            "onlineMode"
        );

    const offlineMode =
        document.getElementById(
            "offlineMode"
        );


    const onlineTitle =
        document.getElementById(
            "onlineTitle"
        );

    const onlineDescription =
        document.getElementById(
            "onlineDescription"
        );


    const videoUrl =
        document.getElementById(
            "videoUrl"
        );

    const platform =
        document.getElementById(
            "platform"
        );

    const thumbnail =
        document.getElementById(
            "thumbnail"
        );


    const offlineTitle =
        document.getElementById(
            "offlineTitle"
        );

    const offlineDescription =
        document.getElementById(
            "offlineDescription"
        );


    const videoFile =
        document.getElementById(
            "videoFile"
        );

    const thumbnailFile =
        document.getElementById(
            "thumbnailFile"
        );


    const metadataLoader =
        document.getElementById(
            "metadataLoader"
        );

    const metadataStatus =
        document.getElementById(
            "metadataStatus"
        );


    const onlinePreview =
        document.getElementById(
            "onlinePreview"
        );

    const previewThumbnail =
        document.getElementById(
            "previewThumbnail"
        );

    const previewTitle =
        document.getElementById(
            "previewTitle"
        );

    const previewDescription =
        document.getElementById(
            "previewDescription"
        );

    const previewPlatform =
        document.getElementById(
            "previewPlatform"
        );


    const uploadProgress =
        document.getElementById(
            "uploadProgress"
        );

    const progressBar =
        document.getElementById(
            "progressBar"
        );

    const progressPercent =
        document.getElementById(
            "progressPercent"
        );

    const progressText =
        document.getElementById(
            "progressText"
        );


    let metadataTimer = null;

    let metadataRequest = null;


    /* =====================================================
       FORM MODE
    ===================================================== */

    function setMode(mode) {

        const online =
            mode === "online";


        typeOptions.forEach(
            (option) => {

                const input =
                    option.querySelector(
                        "input"
                    );


                option.classList.toggle(
                    "active",
                    Boolean(
                        input &&
                        input.checked
                    )
                );

            }
        );


        /* -------------------------------------------------
           ONLINE SECTION
        ------------------------------------------------- */

        if (onlineMode) {

            onlineMode.classList.toggle(
                "hidden",
                !online
            );

            onlineMode.setAttribute(
                "aria-hidden",
                online
                    ? "false"
                    : "true"
            );

        }


        /* -------------------------------------------------
           OFFLINE SECTION
        ------------------------------------------------- */

        if (offlineMode) {

            offlineMode.classList.toggle(
                "hidden",
                online
            );

            offlineMode.setAttribute(
                "aria-hidden",
                online
                    ? "true"
                    : "false"
            );

        }


        /* -------------------------------------------------
           ONLINE FIELDS
        ------------------------------------------------- */

        if (videoUrl) {

            videoUrl.disabled =
                !online;

            videoUrl.required =
                online;

        }


        if (platform) {

            platform.disabled =
                !online;

        }


        if (onlineTitle) {

            onlineTitle.disabled =
                !online;

            onlineTitle.required =
                online;

        }


        if (onlineDescription) {

            onlineDescription.disabled =
                !online;

            onlineDescription.required =
                online;

        }


        /* -------------------------------------------------
           OFFLINE FIELDS
        ------------------------------------------------- */

        if (offlineTitle) {

            offlineTitle.disabled =
                online;

            offlineTitle.required =
                !online;

        }


        if (offlineDescription) {

            offlineDescription.disabled =
                online;

            offlineDescription.required =
                !online;

        }


        if (videoFile) {

            videoFile.disabled =
                online;

            videoFile.required =
                !online;

        }


        if (thumbnailFile) {

            thumbnailFile.disabled =
                online;

        }


        /* -------------------------------------------------
           CLEAR INACTIVE MODE DATA
        ------------------------------------------------- */

        if (online) {

            if (offlineTitle) {

                offlineTitle.value =
                    "";

            }


            if (offlineDescription) {

                offlineDescription.value =
                    "";

            }


            if (videoFile) {

                videoFile.value =
                    "";

            }


            if (thumbnailFile) {

                thumbnailFile.value =
                    "";

            }


            if (uploadProgress) {

                uploadProgress.classList.remove(
                    "show"
                );

            }

        } else {

            if (onlineTitle) {

                onlineTitle.value =
                    "";

            }


            if (onlineDescription) {

                onlineDescription.value =
                    "";

            }


            if (videoUrl) {

                videoUrl.value =
                    "";

            }


            if (thumbnail) {

                thumbnail.value =
                    "";

            }


            if (onlinePreview) {

                onlinePreview.classList.remove(
                    "show"
                );

            }


            if (metadataStatus) {

                metadataStatus.textContent =
                    "";

                metadataStatus.classList.remove(
                    "error"
                );

            }


            cancelMetadataRequest();

        }

    }


    /* =====================================================
       CANCEL PREVIOUS METADATA REQUEST
    ===================================================== */

    function cancelMetadataRequest() {

        if (
            metadataRequest &&
            typeof metadataRequest.abort === "function"
        ) {

            try {

                metadataRequest.abort();

            } catch (error) {
                /* Ignore abort errors */
            }

        }

        metadataRequest = null;

    }


    /* =====================================================
       TYPE CHANGE
    ===================================================== */

    typeOptions.forEach(
        (option) => {

            const input =
                option.querySelector(
                    "input"
                );


            if (!input) {
                return;
            }


            input.addEventListener(
                "change",
                () => {

                    setMode(
                        input.value
                    );

                }
            );

        }
    );


    /* =====================================================
       INITIAL MODE
    ===================================================== */

    const checkedType =
        bayanForm.querySelector(
            'input[name="upload_type"]:checked'
        );


    setMode(
        checkedType
            ? checkedType.value
            : "online"
    );


    /* =====================================================
       LOAD VIDEO METADATA
    ===================================================== */

    async function loadMetadata() {

        if (
            !videoUrl ||
            !platform
        ) {

            return;

        }


        const url =
            videoUrl.value.trim();


        if (!url) {

            cancelMetadataRequest();


            if (onlinePreview) {

                onlinePreview.classList.remove(
                    "show"
                );

            }


            if (metadataStatus) {

                metadataStatus.textContent =
                    "";

                metadataStatus.classList.remove(
                    "error"
                );

            }

            return;

        }


        cancelMetadataRequest();


        if (metadataLoader) {

            metadataLoader.style.display =
                "block";

        }


        if (metadataStatus) {

            metadataStatus.classList.remove(
                "error"
            );

            metadataStatus.textContent =
                "Loading video information...";

        }


        const controller =
            new AbortController();


        metadataRequest =
            controller;


        try {

            const response =
                await fetch(
                    "/admin/bayans/preview",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "X-Requested-With":
                                "XMLHttpRequest"
                        },

                        body: JSON.stringify({
                            url: url,
                            platform:
                                platform.value
                        }),

                        signal:
                            controller.signal
                    }
                );


            let data = null;


            try {

                data =
                    await response.json();

            } catch (error) {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Could not load video information."
                );

            }


            /* -------------------------------------------------
               ONLY UPDATE IF URL IS STILL THE SAME
            ------------------------------------------------- */

            if (
                videoUrl.value.trim() !== url
            ) {

                return;

            }


            if (onlineTitle) {

                onlineTitle.value =
                    data.title ||
                    "";

            }


            if (onlineDescription) {

                onlineDescription.value =
                    data.description ||
                    "";

            }


            if (thumbnail) {

                thumbnail.value =
                    data.thumbnail ||
                    "";

            }


            if (previewTitle) {

                previewTitle.textContent =
                    data.title ||
                    "Bayan";

            }


            if (previewDescription) {

                previewDescription.textContent =
                    data.description ||
                    "No description available.";

            }


            if (previewPlatform) {

                previewPlatform.textContent =
                    platform.value ||
                    "Online";

            }


            if (
                previewThumbnail &&
                data.thumbnail
            ) {

                previewThumbnail.src =
                    data.thumbnail;


                previewThumbnail.onerror =
                    () => {

                        if (onlinePreview) {

                            onlinePreview.classList.remove(
                                "show"
                            );

                        }

                    };


                if (onlinePreview) {

                    onlinePreview.classList.add(
                        "show"
                    );

                }

            } else {

                if (onlinePreview) {

                    onlinePreview.classList.remove(
                        "show"
                    );

                }

            }


            if (metadataStatus) {

                metadataStatus.textContent =
                    "Video information loaded.";

                metadataStatus.classList.remove(
                    "error"
                );

            }

        } catch (error) {

            /*
             * AbortController cancellation is normal when
             * the user changes the URL quickly.
             */

            if (
                error.name ===
                "AbortError"
            ) {

                return;

            }


            if (metadataStatus) {

                metadataStatus.classList.add(
                    "error"
                );

                metadataStatus.textContent =
                    error.message ||
                    "Could not load video information.";

            }


            if (onlinePreview) {

                onlinePreview.classList.remove(
                    "show"
                );

            }

        } finally {

            if (
                metadataRequest ===
                controller
            ) {

                metadataRequest =
                    null;

            }


            if (metadataLoader) {

                metadataLoader.style.display =
                    "none";

            }

        }

    }


    /* =====================================================
       VIDEO URL INPUT
    ===================================================== */

    if (videoUrl) {

        videoUrl.addEventListener(
            "input",
            () => {

                clearTimeout(
                    metadataTimer
                );


                if (metadataStatus) {

                    metadataStatus.classList.remove(
                        "error"
                    );

                }


                metadataTimer =
                    setTimeout(
                        loadMetadata,
                        700
                    );

            }
        );

    }


    /* =====================================================
       PLATFORM CHANGE
    ===================================================== */

    if (platform) {

        platform.addEventListener(
            "change",
            () => {

                if (
                    videoUrl &&
                    videoUrl.value.trim()
                ) {

                    clearTimeout(
                        metadataTimer
                    );


                    metadataTimer =
                        setTimeout(
                            loadMetadata,
                            200
                        );

                }

            }
        );

    }


    /* =====================================================
       VIDEO UPLOAD PROGRESS
    ===================================================== */

    bayanForm.addEventListener(
        "submit",
        (event) => {

            const selectedType =
                bayanForm.querySelector(
                    'input[name="upload_type"]:checked'
                );


            /*
             * Online Bayan:
             * Let the browser submit normally.
             */

            if (
                !selectedType ||
                selectedType.value !== "upload"
            ) {

                return;

            }


            /*
             * Uploaded Bayan:
             * Use AJAX/XHR so progress can be displayed.
             */

            event.preventDefault();


            if (!videoFile) {

                bayanForm.reportValidity();

                return;

            }


            const file =
                videoFile.files[0];


            if (!file) {

                bayanForm.reportValidity();

                return;

            }


            /* -------------------------------------------------
               RESET PROGRESS UI
            ------------------------------------------------- */

            if (uploadProgress) {

                uploadProgress.classList.add(
                    "show"
                );

            }


            if (progressBar) {

                progressBar.style.width =
                    "0%";

            }


            if (progressPercent) {

                progressPercent.textContent =
                    "0%";

            }


            if (progressText) {

                progressText.textContent =
                    "Starting upload...";

            }


            /* -------------------------------------------------
               XHR
            ------------------------------------------------- */

            const xhr =
                new XMLHttpRequest();


            xhr.open(
                "POST",
                bayanForm.action ||
                window.location.href
            );


            xhr.setRequestHeader(
                "X-Requested-With",
                "XMLHttpRequest"
            );


            /* -------------------------------------------------
               UPLOAD PROGRESS
            ------------------------------------------------- */

            xhr.upload.addEventListener(
                "progress",
                (event) => {

                    if (
                        !event.lengthComputable
                    ) {

                        return;

                    }


                    const percent =
                        Math.round(
                            (
                                event.loaded /
                                event.total
                            ) * 100
                        );


                    if (progressBar) {

                        progressBar.style.width =
                            `${percent}%`;

                    }


                    if (progressPercent) {

                        progressPercent.textContent =
                            `${percent}%`;

                    }


                    if (progressText) {

                        progressText.textContent =
                            percent < 100
                                ? "Uploading video..."
                                : "Processing video...";

                    }

                }
            );


            /* -------------------------------------------------
               SUCCESS / SERVER RESPONSE
            ------------------------------------------------- */

            xhr.addEventListener(
                "load",
                () => {

                    if (
                        xhr.status >= 200 &&
                        xhr.status < 400
                    ) {

                        if (progressBar) {

                            progressBar.style.width =
                                "100%";

                        }


                        if (progressPercent) {

                            progressPercent.textContent =
                                "100%";

                        }


                        if (progressText) {

                            progressText.textContent =
                                "Upload complete.";

                        }


                        let redirectUrl =
                            "/admin/bayans";


                        /*
                         * Backend may return:
                         * { "redirect": "/admin/bayans" }
                         *
                         * If it returns normal HTML,
                         * use the default admin Bayans URL.
                         */

                        try {

                            const response =
                                JSON.parse(
                                    xhr.responseText
                                );


                            if (
                                response &&
                                response.redirect
                            ) {

                                redirectUrl =
                                    response.redirect;

                            }

                        } catch (error) {

                            /*
                             * HTML response is acceptable.
                             * Keep default redirect.
                             */

                        }


                        setTimeout(
                            () => {

                                window.location.href =
                                    redirectUrl;

                            },
                            450
                        );

                    } else {

                        if (uploadProgress) {

                            uploadProgress.classList.add(
                                "show"
                            );

                        }


                        if (progressText) {

                            progressText.textContent =
                                "Upload failed. Please try again.";

                        }

                    }

                }
            );


            /* -------------------------------------------------
               NETWORK ERROR
            ------------------------------------------------- */

            xhr.addEventListener(
                "error",
                () => {

                    if (progressText) {

                        progressText.textContent =
                            "Upload failed. Please check your connection and try again.";

                    }

                }
            );


            /* -------------------------------------------------
               UPLOAD ABORTED
            ------------------------------------------------- */

            xhr.addEventListener(
                "abort",
                () => {

                    if (progressText) {

                        progressText.textContent =
                            "Upload cancelled.";

                    }

                }
            );


            /* -------------------------------------------------
               SEND FORM
            ------------------------------------------------- */

            const formData =
                new FormData(
                    bayanForm
                );


            xhr.send(
                formData
            );

        }
    );

}


/* =========================================================
   BOOK ORDER FORM
========================================================= */

function initBookOrderForm(
    form
) {

    const fullName =
        document.getElementById(
            "fullName"
        );

    const mobileNumber =
        document.getElementById(
            "mobileNumber"
        );

    const alternateNumber =
        document.getElementById(
            "alternateNumber"
        );

    const address =
        document.getElementById(
            "address"
        );

    const district =
        document.getElementById(
            "district"
        );

    const state =
        document.getElementById(
            "state"
        );

    const pinCode =
        document.getElementById(
            "pinCode"
        );

    const countryCode =
        document.getElementById(
            "countryCode"
        );

    const alternateCountryCode =
        document.getElementById(
            "alternateCountryCode"
        );

    const whatsappError =
        document.getElementById(
            "orderWhatsappError"
        );


    /* =====================================================
       SERVER-SIDE BOOK DATA
    ===================================================== */

    const whatsappNumber =
        form.dataset.whatsappNumber ||
        "";

    const bookTitle =
        form.dataset.bookTitle ||
        "";

    const bookAuthor =
        form.dataset.bookAuthor ||
        "";

    const bookPrice =
        form.dataset.bookPrice ||
        "Price on request";


    /* =====================================================
       ERROR HELPERS
    ===================================================== */

    function getErrorElement(
        element
    ) {

        if (
            !element ||
            !element.id
        ) {

            return null;

        }


        return document.getElementById(
            `${element.id}Error`
        );

    }


    function setError(
        element,
        message
    ) {

        if (!element) {
            return;
        }


        const error =
            getErrorElement(
                element
            );


        if (error) {

            error.textContent =
                message;

        }


        element.classList.add(
            "input-error"
        );

        element.setAttribute(
            "aria-invalid",
            "true"
        );

    }


    function clearError(
        element
    ) {

        if (!element) {
            return;
        }


        const error =
            getErrorElement(
                element
            );


        if (error) {

            error.textContent =
                "";

        }


        element.classList.remove(
            "input-error"
        );

        element.removeAttribute(
            "aria-invalid"
        );

    }


    /* =====================================================
       PHONE VALIDATION
    ===================================================== */

    function isValidPhone(
        value
    ) {

        const digits =
            String(
                value || ""
            ).replace(
                /\D/g,
                ""
            );


        return (
            digits.length >= 7 &&
            digits.length <= 15
        );

    }


    /* =====================================================
       VALIDATION
    ===================================================== */

    function validate() {

        let valid = true;


        [
            fullName,
            mobileNumber,
            alternateNumber,
            address,
            district,
            state,
            pinCode
        ].forEach(
            clearError
        );


        /* -------------------------------------------------
           FULL NAME
        ------------------------------------------------- */

        if (
            !fullName ||
            fullName.value.trim().length < 2
        ) {

            setError(
                fullName,
                "Please enter your full name."
            );

            valid = false;

        }


        /* -------------------------------------------------
           MOBILE
        ------------------------------------------------- */

        if (
            !mobileNumber ||
            !isValidPhone(
                mobileNumber.value
            )
        ) {

            setError(
                mobileNumber,
                "Please enter a valid mobile number."
            );

            valid = false;

        }


        /* -------------------------------------------------
           ALTERNATE MOBILE
        ------------------------------------------------- */

        if (
            alternateNumber &&
            alternateNumber.value.trim() &&
            !isValidPhone(
                alternateNumber.value
            )
        ) {

            setError(
                alternateNumber,
                "Please enter a valid alternate number."
            );

            valid = false;

        }


        /* -------------------------------------------------
           ADDRESS
        ------------------------------------------------- */

        if (
            !address ||
            address.value.trim().length < 5
        ) {

            setError(
                address,
                "Please enter your complete delivery address."
            );

            valid = false;

        }


        /* -------------------------------------------------
           DISTRICT
        ------------------------------------------------- */

        if (
            !district ||
            district.value.trim().length < 2
        ) {

            setError(
                district,
                "Please enter your district."
            );

            valid = false;

        }


        /* -------------------------------------------------
           STATE
        ------------------------------------------------- */

        if (
            !state ||
            !state.value
        ) {

            setError(
                state,
                "Please select your state or UT."
            );

            valid = false;

        }


        /* -------------------------------------------------
           PIN CODE
        ------------------------------------------------- */

        if (
            !pinCode ||
            !/^\d{6}$/.test(
                pinCode.value.trim()
            )
        ) {

            setError(
                pinCode,
                "Please enter a valid 6-digit PIN code."
            );

            valid = false;

        }


        return valid;

    }


    /* =====================================================
       NUMBER-ONLY INPUTS
    ===================================================== */

    [
        mobileNumber,
        alternateNumber,
        pinCode
    ].forEach(
        (element) => {

            if (!element) {
                return;
            }


            element.addEventListener(
                "input",
                () => {

                    element.value =
                        element.value.replace(
                            /\D/g,
                            ""
                        );

                }
            );

        }
    );


    /* =====================================================
       CLEAR ERROR WHEN USER TYPES
    ===================================================== */

    [
        fullName,
        mobileNumber,
        alternateNumber,
        address,
        district,
        state,
        pinCode
    ].forEach(
        (element) => {

            if (!element) {
                return;
            }


            element.addEventListener(
                "input",
                () => {

                    clearError(
                        element
                    );

                }
            );


            element.addEventListener(
                "change",
                () => {

                    clearError(
                        element
                    );

                }
            );

        }
    );


    /* =====================================================
       HIDE WHATSAPP ERROR WHEN USER RETRIES
    ===================================================== */

    function clearWhatsappError() {

        if (whatsappError) {

            whatsappError.hidden =
                true;

        }

    }


    [
        fullName,
        mobileNumber,
        alternateNumber,
        address,
        district,
        state,
        pinCode
    ].forEach(
        (element) => {

            if (!element) {
                return;
            }


            element.addEventListener(
                "input",
                clearWhatsappError
            );


            element.addEventListener(
                "change",
                clearWhatsappError
            );

        }
    );


    /* =====================================================
       SUBMIT
    ===================================================== */

    form.addEventListener(
        "submit",
        (event) => {

            event.preventDefault();


            /* -------------------------------------------------
               VALIDATE CUSTOMER DATA
            ------------------------------------------------- */

            if (!validate()) {

                const firstError =
                    form.querySelector(
                        ".input-error"
                    );


                if (firstError) {

                    firstError.focus();

                }

                return;

            }


            /* -------------------------------------------------
               CHECK WHATSAPP NUMBER
            ------------------------------------------------- */

            const cleanWhatsapp =
                String(
                    whatsappNumber
                ).replace(
                    /\D/g,
                    ""
                );


            if (!cleanWhatsapp) {

                if (whatsappError) {

                    whatsappError.hidden =
                        false;

                }

                return;

            }


            /* -------------------------------------------------
               COUNTRY CODES
            ------------------------------------------------- */

            const selectedCountryCode =
                countryCode
                    ? countryCode.value
                    : "+91";


            const selectedAlternateCountryCode =
                alternateCountryCode
                    ? alternateCountryCode.value
                    : "+91";


            /* =================================================
               CREATE WHATSAPP MESSAGE
            ================================================= */

            let message = "";


            message +=
                "BOOK ORDER REQUEST\n\n";


            /* -------------------------------------------------
               BOOK DETAILS
            ------------------------------------------------- */

            message +=
                "BOOK DETAILS\n";


            message +=
                "Book: "
                + bookTitle
                + "\n";


            message +=
                "Author: "
                + bookAuthor
                + "\n";


            message +=
                "Price: "
                + bookPrice
                + "\n";


            /* -------------------------------------------------
               CUSTOMER DETAILS
            ------------------------------------------------- */

            message +=
                "\nCUSTOMER DETAILS\n";


            message +=
                "Name: "
                + fullName.value.trim()
                + "\n";


            message +=
                "Mobile: "
                + selectedCountryCode
                + " "
                + mobileNumber.value.trim()
                + "\n";


            if (
                alternateNumber &&
                alternateNumber.value.trim()
            ) {

                message +=
                    "Alternate Mobile: "
                    + selectedAlternateCountryCode
                    + " "
                    + alternateNumber.value.trim()
                    + "\n";

            }


            /* -------------------------------------------------
               DELIVERY ADDRESS
            ------------------------------------------------- */

            message +=
                "\nDELIVERY ADDRESS\n";


            message +=
                "Address: "
                + address.value.trim()
                + "\n";


            message +=
                "District: "
                + district.value.trim()
                + "\n";


            message +=
                "State/UT: "
                + state.value
                + "\n";


            message +=
                "PIN Code: "
                + pinCode.value.trim()
                + "\n";


            message +=
                "\nPlease confirm this book order.";


            /* =================================================
               WHATSAPP URL
            ================================================= */

            const whatsappUrl =
                "https://wa.me/"
                + cleanWhatsapp
                + "?text="
                + encodeURIComponent(
                    message
                );


            /* =================================================
               PREVENT DOUBLE CLICK
            ================================================= */

            const submitButton =
                form.querySelector(
                    ".order-submit"
                );


            if (submitButton) {

                submitButton.disabled =
                    true;

                submitButton.setAttribute(
                    "aria-disabled",
                    "true"
                );

                submitButton.innerHTML =
                    '<i class="fa-brands fa-whatsapp"></i> Opening WhatsApp...';

            }


            /* =================================================
               OPEN WHATSAPP
            ================================================= */

            window.location.href =
                whatsappUrl;

        }
    );

}
