document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       HELPERS
    ========================================= */

    function getCsrfToken(form = null) {

        if (form) {

            const input =
                form.querySelector(
                    'input[name="csrf_token"]'
                );

            if (input && input.value) {
                return input.value;
            }
        }

        const meta =
            document.querySelector(
                'meta[name="csrf-token"]'
            );

        if (meta && meta.content) {
            return meta.content;
        }

        return "";
    }


    function setCsrfHeader(xhr, form = null) {

        const token =
            getCsrfToken(form);

        if (token) {

            xhr.setRequestHeader(
                "X-CSRFToken",
                token
            );
        }
    }


    function getSafeRedirect(value) {

        if (!value) {
            return null;
        }

        try {

            const url =
                new URL(
                    value,
                    window.location.origin
                );

            if (
                url.protocol !== "http:" &&
                url.protocol !== "https:"
            ) {
                return null;
            }

            if (
                url.origin !==
                window.location.origin
            ) {
                return null;
            }

            return url.href;

        } catch (error) {

            return null;
        }
    }


    function isSafeHttpUrl(value) {

        if (!value) {
            return false;
        }

        try {

            const url =
                new URL(value);

            return (
                (
                    url.protocol === "http:" ||
                    url.protocol === "https:"
                ) &&
                !url.username &&
                !url.password
            );

        } catch (error) {

            return false;
        }
    }


    /* =========================================
       ADMIN SIDEBAR
    ========================================= */

    const adminSidebar =
        document.getElementById(
            "adminSidebar"
        );

    const adminSidebarToggle =
        document.getElementById(
            "adminSidebarToggle"
        );

    const adminSidebarOverlay =
        document.getElementById(
            "adminSidebarOverlay"
        );


    function openSidebar() {

        if (!adminSidebar) {
            return;
        }

        adminSidebar.classList.add("open");
        adminSidebar.classList.add("active");

        if (adminSidebarOverlay) {

            adminSidebarOverlay.classList.add("show");
            adminSidebarOverlay.classList.add("active");

        }

        if (adminSidebarToggle) {

            adminSidebarToggle.classList.add("active");

            adminSidebarToggle.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        document.body.classList.add(
            "sidebar-open"
        );
    }


    function closeSidebar() {

        if (!adminSidebar) {
            return;
        }

        adminSidebar.classList.remove("open");
        adminSidebar.classList.remove("active");

        if (adminSidebarOverlay) {

            adminSidebarOverlay.classList.remove("show");
            adminSidebarOverlay.classList.remove("active");

        }

        if (adminSidebarToggle) {

            adminSidebarToggle.classList.remove("active");

            adminSidebarToggle.setAttribute(
                "aria-expanded",
                "false"
            );
        }

        document.body.classList.remove(
            "sidebar-open"
        );
    }


    if (adminSidebarToggle) {

        adminSidebarToggle.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                if (
                    adminSidebar &&
                    adminSidebar.classList.contains("open")
                ) {

                    closeSidebar();

                } else {

                    openSidebar();

                }
            }
        );
    }


    if (adminSidebarOverlay) {

        adminSidebarOverlay.addEventListener(
            "click",
            closeSidebar
        );
    }


    document
        .querySelectorAll(".admin-sidebar a")
        .forEach((link) => {

            link.addEventListener(
                "click",
                closeSidebar
            );

        });


    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "Escape") {

                closeSidebar();

            }

        }
    );


    /* =========================================
       FLASH MESSAGE CLOSE
    ========================================= */

    document
        .querySelectorAll("[data-flash-close]")
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const flash =
                        button.closest(
                            "[data-flash]"
                        );

                    if (flash) {
                        flash.remove();
                    }
                }
            );
        });


    /* =========================================
       BOOK FORM
    ========================================= */

    const bookForm =
        document.querySelector(
            "[data-book-form]"
        );

    const bookType =
        document.getElementById(
            "bookType"
        );


    if (bookForm && bookType) {

        initBookForm(
            bookForm
        );
    }


    function initBookForm(form) {

        const readField =
            form.querySelector(
                "[data-read-field]"
            );

        const sellField =
            form.querySelector(
                "[data-sell-field]"
            );

        const pdfInput =
            form.querySelector(
                "[data-pdf-input]"
            );

        const priceInput =
            form.querySelector(
                "[data-price-input]"
            );

        const uploadInput =
            form.querySelector(
                "[data-upload-input]"
            );

        const submitButton =
            form.querySelector(
                "[data-submit-button]"
            );

        const progress =
            form.querySelector(
                "[data-upload-progress]"
            );

        const progressBar =
            form.querySelector(
                "[data-upload-bar]"
            );

        const progressPercent =
            form.querySelector(
                "[data-upload-percent]"
            );

        const progressStatus =
            form.querySelector(
                "[data-upload-status]"
            );

        const successPopup =
            document.querySelector(
                "[data-upload-success-popup]"
            );


        /* -------------------------------------
           BOOK TYPE SWITCH
        ------------------------------------- */

        function updateBookType() {

            const selectedType =
                bookType.value;


            const isRead =
                selectedType === "read";

            const isOrder =
                selectedType === "order";


            /* Read Online */

            if (readField) {

                readField.hidden =
                    !isRead;
            }


            if (pdfInput) {

                pdfInput.disabled =
                    !isRead;

                pdfInput.required =
                    isRead;

            }


            /* Sell / Delivery */

            if (sellField) {

                sellField.hidden =
                    !isOrder;
            }


            if (priceInput) {

                priceInput.disabled =
                    !isOrder;

                priceInput.required =
                    isOrder;

            }


            /* Clear inactive field */

            if (!isRead && pdfInput) {

                pdfInput.value = "";

            }


            if (!isOrder && priceInput) {

                priceInput.value = "";

            }
        }


        bookType.addEventListener(
            "change",
            updateBookType
        );


        updateBookType();


        /* -------------------------------------
           SUCCESS POPUP
        ------------------------------------- */

        function showSuccessPopup() {

            if (!successPopup) {
                return;
            }

            successPopup.hidden = false;

            requestAnimationFrame(() => {

                successPopup.classList.add(
                    "show"
                );

            });
        }


        /* -------------------------------------
           BOOK UPLOAD
        ------------------------------------- */

        form.addEventListener(
            "submit",
            (event) => {

                event.preventDefault();


                const selectedType =
                    bookType.value;


                if (
                    selectedType === "read" &&
                    (
                        !pdfInput ||
                        !pdfInput.files ||
                        !pdfInput.files.length
                    )
                ) {

                    alert(
                        "Please select the book PDF."
                    );

                    return;
                }


                if (
                    selectedType === "order" &&
                    (
                        !priceInput ||
                        !priceInput.value.trim()
                    )
                ) {

                    alert(
                        "Please enter the book price."
                    );

                    return;
                }


                if (
                    !uploadInput ||
                    !uploadInput.files ||
                    !uploadInput.files.length
                ) {

                    alert(
                        "Please select the book cover image."
                    );

                    return;
                }


                if (progress) {

                    progress.hidden = false;

                }


                if (submitButton) {

                    submitButton.disabled = true;

                }


                if (progressStatus) {

                    progressStatus.textContent =
                        "Uploading book...";

                }


                const formData =
                    new FormData(form);


                const xhr =
                    new XMLHttpRequest();


                xhr.open(
                    "POST",
                    form.action ||
                    window.location.href,
                    true
                );


                xhr.setRequestHeader(
                    "X-Requested-With",
                    "XMLHttpRequest"
                );


                xhr.setRequestHeader(
                    "Accept",
                    "application/json"
                );


                setCsrfHeader(
                    xhr,
                    form
                );


                xhr.upload.onprogress =
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
                                ) *
                                100
                            );


                        if (progressBar) {

                            progressBar.style.width =
                                `${percent}%`;

                        }


                        if (progressPercent) {

                            progressPercent.textContent =
                                `${percent}%`;

                        }


                        if (progressStatus) {

                            progressStatus.textContent =
                                percent >= 100
                                    ? "Processing book..."
                                    : "Uploading book...";

                        }
                    };


                xhr.onload =
                    () => {

                        let data = null;


                        try {

                            data =
                                JSON.parse(
                                    xhr.responseText
                                );

                        } catch (error) {

                            data = null;

                        }


                        /* ---------------------------------
                           SUCCESS
                        --------------------------------- */

                        if (
                            xhr.status >= 200 &&
                            xhr.status < 300 &&
                            data &&
                            data.success
                        ) {

                            if (progressBar) {

                                progressBar.style.width =
                                    "100%";

                            }


                            if (progressPercent) {

                                progressPercent.textContent =
                                    "100%";

                            }


                            if (progressStatus) {

                                progressStatus.textContent =
                                    "Upload complete.";

                            }


                            showSuccessPopup();


                            /*
                             * Give the user enough time
                             * to see the success popup.
                             */

                            setTimeout(
                                () => {

                                    const redirect =
                                        getSafeRedirect(
                                            data.redirect
                                        );


                                    if (redirect) {

                                        window.location.href =
                                            redirect;

                                    } else {

                                        window.location.reload();

                                    }

                                },
                                1500
                            );


                            return;
                        }


                        /* ---------------------------------
                           VALIDATION / SERVER ERROR
                        --------------------------------- */

                        if (submitButton) {

                            submitButton.disabled =
                                false;

                        }


                        if (progress) {

                            progress.hidden =
                                true;

                        }


                        const message =
                            data &&
                            data.message
                                ? data.message
                                : "Book could not be uploaded.";


                        alert(message);

                    };


                xhr.onerror =
                    () => {

                        if (submitButton) {

                            submitButton.disabled =
                                false;

                        }


                        if (progress) {

                            progress.hidden =
                                true;

                        }


                        alert(
                            "Upload failed. Please check your connection and try again."
                        );
                    };


                xhr.send(
                    formData
                );
            }
        );
    }


    /* =========================================
       BAYAN FORM
       Existing Bayan functionality preserved
    ========================================= */

    const bayanForm =
        document.getElementById(
            "bayanForm"
        );


    if (bayanForm) {

        initBayanForm(
            bayanForm
        );
    }


    function initBayanForm(form) {

        const radios =
            form.querySelectorAll(
                'input[name="upload_type"]'
            );

        const typeOptions =
            form.querySelectorAll(
                "[data-upload-type]"
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


        function setOnlineFields(enabled) {

            if (platform) {
                platform.disabled = !enabled;
            }

            if (videoUrl) {
                videoUrl.disabled = !enabled;
            }

            if (onlineTitle) {
                onlineTitle.disabled = !enabled;
                onlineTitle.required = enabled;
            }

            if (onlineDescription) {
                onlineDescription.disabled = !enabled;
            }
        }


        function setOfflineFields(enabled) {

            if (offlineTitle) {
                offlineTitle.disabled = !enabled;
                offlineTitle.required = enabled;
            }

            if (offlineDescription) {
                offlineDescription.disabled = !enabled;
                offlineDescription.required = enabled;
            }

            if (videoFile) {
                videoFile.disabled = !enabled;
                videoFile.required = enabled;
            }

            if (thumbnailFile) {
                thumbnailFile.disabled = !enabled;
            }
        }


        function updateBayanMode() {

            const selected =
                form.querySelector(
                    'input[name="upload_type"]:checked'
                );


            if (!selected) {
                return;
            }


            const isOnline =
                selected.value === "online";


            if (onlineMode) {

                onlineMode.classList.toggle(
                    "hidden",
                    !isOnline
                );

                onlineMode.setAttribute(
                    "aria-hidden",
                    isOnline ? "false" : "true"
                );
            }


            if (offlineMode) {

                offlineMode.classList.toggle(
                    "hidden",
                    isOnline
                );

                offlineMode.setAttribute(
                    "aria-hidden",
                    isOnline ? "true" : "false"
                );
            }


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


            setOnlineFields(
                isOnline
            );

            setOfflineFields(
                !isOnline
            );


            if (isOnline) {

                if (offlineTitle) {
                    offlineTitle.value = "";
                }

                if (offlineDescription) {
                    offlineDescription.value = "";
                }

                if (videoFile) {
                    videoFile.value = "";
                }

                if (thumbnailFile) {
                    thumbnailFile.value = "";
                }

            } else {

                if (onlineTitle) {
                    onlineTitle.value = "";
                }

                if (onlineDescription) {
                    onlineDescription.value = "";
                }

                if (videoUrl) {
                    videoUrl.value = "";
                }
            }
        }


        radios.forEach(
            (radio) => {

                radio.addEventListener(
                    "change",
                    updateBayanMode
                );

            }
        );


        updateBayanMode();


        /* -------------------------------------
           METADATA
        ------------------------------------- */

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

        const thumbnail =
            document.getElementById(
                "thumbnail"
            );


        let metadataTimer = null;
        let metadataController = null;


        function setMetadataLoading(loading) {

            if (metadataLoader) {

                metadataLoader.classList.toggle(
                    "show",
                    loading
                );
            }

            if (videoUrl) {

                videoUrl.classList.toggle(
                    "loading",
                    loading
                );
            }
        }


        function setMetadataStatus(
            message,
            type = ""
        ) {

            if (!metadataStatus) {
                return;
            }

            metadataStatus.textContent =
                message;

            metadataStatus.className =
                "metadata-status";


            if (type) {

                metadataStatus.classList.add(
                    type
                );
            }
        }


        function updatePreview(data) {

            if (!data) {
                return;
            }


            if (previewPlatform) {

                previewPlatform.textContent =
                    data.platform ||
                    (
                        platform
                            ? platform.value
                            : ""
                    ) ||
                    "Video";
            }


            if (previewTitle) {

                previewTitle.textContent =
                    data.title ||
                    "Video preview";
            }


            if (previewDescription) {

                previewDescription.textContent =
                    data.description ||
                    "Video title and description will appear here.";
            }


            if (
                previewThumbnail &&
                data.thumbnail &&
                isSafeHttpUrl(
                    data.thumbnail
                )
            ) {

                previewThumbnail.src =
                    data.thumbnail;

                previewThumbnail.alt =
                    data.title ||
                    "Video thumbnail";

                previewThumbnail.referrerPolicy =
                    "no-referrer";


                if (onlinePreview) {

                    onlinePreview.classList.add(
                        "show"
                    );
                }
            }


            if (
                onlineTitle &&
                data.title
            ) {

                onlineTitle.value =
                    String(
                        data.title
                    ).slice(
                        0,
                        35
                    );
            }


            if (
                onlineDescription &&
                data.description
            ) {

                onlineDescription.value =
                    String(
                        data.description
                    ).slice(
                        0,
                        500
                    );
            }


            if (
                thumbnail &&
                data.thumbnail &&
                isSafeHttpUrl(
                    data.thumbnail
                )
            ) {

                thumbnail.value =
                    data.thumbnail;
            }
        }


        async function fetchMetadata() {

            if (!videoUrl) {
                return;
            }


            const url =
                videoUrl.value.trim();


            if (!url) {

                setMetadataStatus("");

                if (onlinePreview) {

                    onlinePreview.classList.remove(
                        "show"
                    );
                }

                return;
            }


            if (!isSafeHttpUrl(url)) {

                setMetadataStatus(
                    "Enter a valid HTTP or HTTPS video URL.",
                    "error"
                );

                return;
            }


            if (metadataController) {

                metadataController.abort();
            }


            metadataController =
                new AbortController();


            setMetadataLoading(true);

            setMetadataStatus(
                "Loading video details..."
            );


            try {

                const csrfToken =
                    getCsrfToken(form);


                if (!csrfToken) {

                    throw new Error(
                        "Security token is missing. Please refresh the page."
                    );
                }


                const response =
                    await fetch(
                        "/admin/bayans/preview",
                        {
                            method: "POST",
                            credentials: "same-origin",
                            referrerPolicy: "no-referrer",
                            signal: metadataController.signal,

                            headers: {
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                "X-Requested-With": "XMLHttpRequest",
                                "X-CSRFToken": csrfToken
                            },

                            body:
                                JSON.stringify({
                                    url: url,
                                    platform:
                                        platform
                                            ? platform.value
                                            : "Other"
                                })
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.message ||
                        "Video details could not be loaded."
                    );
                }


                updatePreview(data);


                setMetadataStatus(
                    data.message ||
                    "Video details loaded.",
                    "success"
                );


            } catch (error) {

                if (
                    error.name ===
                    "AbortError"
                ) {
                    return;
                }


                setMetadataStatus(
                    error.message ||
                    "Could not load video details.",
                    "error"
                );

            } finally {

                setMetadataLoading(false);
            }
        }


        function scheduleMetadataFetch() {

            clearTimeout(
                metadataTimer
            );

            metadataTimer =
                setTimeout(
                    fetchMetadata,
                    700
                );
        }


        if (videoUrl) {

            videoUrl.addEventListener(
                "input",
                scheduleMetadataFetch
            );

            videoUrl.addEventListener(
                "blur",
                fetchMetadata
            );
        }


        if (platform) {

            platform.addEventListener(
                "change",
                () => {

                    if (
                        videoUrl &&
                        videoUrl.value.trim()
                    ) {

                        fetchMetadata();
                    }
                }
            );
        }


        /* -------------------------------------
           BAYAN SUBMIT
        ------------------------------------- */

        form.addEventListener(
            "submit",
            handleBayanSubmit
        );


        function handleBayanSubmit(event) {

            const selected =
                form.querySelector(
                    'input[name="upload_type"]:checked'
                );


            if (!selected) {
                return;
            }


            if (
                selected.value !==
                "upload"
            ) {
                return;
            }


            event.preventDefault();


            if (
                !videoFile ||
                !videoFile.files ||
                !videoFile.files.length
            ) {

                alert(
                    "Please select a video file."
                );

                return;
            }


            uploadBayanForm();
        }


        function uploadBayanForm() {

            const progress =
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

            const submitButton =
                form.querySelector(
                    "[data-submit-button]"
                );


            if (progress) {
                progress.hidden = false;
            }

            if (submitButton) {
                submitButton.disabled = true;
            }


            const formData =
                new FormData(form);


            const xhr =
                new XMLHttpRequest();


            xhr.open(
                "POST",
                form.action ||
                window.location.href,
                true
            );


            xhr.setRequestHeader(
                "X-Requested-With",
                "XMLHttpRequest"
            );


            setCsrfHeader(
                xhr,
                form
            );


            xhr.upload.onprogress =
                function (event) {

                    if (!event.lengthComputable) {
                        return;
                    }


                    const percent =
                        Math.round(
                            (
                                event.loaded /
                                event.total
                            ) *
                            100
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
                            percent >= 100
                                ? "Processing video..."
                                : "Uploading video...";
                    }
                };


            xhr.onload =
                function () {

                    if (
                        xhr.status >= 200 &&
                        xhr.status < 400
                    ) {

                        try {

                            const data =
                                JSON.parse(
                                    xhr.responseText
                                );


                            if (data.redirect) {

                                const redirect =
                                    getSafeRedirect(
                                        data.redirect
                                    );


                                if (redirect) {

                                    window.location.href =
                                        redirect;

                                    return;
                                }
                            }


                            window.location.reload();

                            return;

                        } catch (error) {

                            window.location.reload();

                            return;
                        }
                    }


                    if (submitButton) {
                        submitButton.disabled = false;
                    }


                    if (progressText) {

                        progressText.textContent =
                            "Upload failed. Please try again.";
                    }
                };


            xhr.onerror =
                function () {

                    if (submitButton) {
                        submitButton.disabled = false;
                    }


                    if (progressText) {

                        progressText.textContent =
                            "Upload failed. Please check your connection.";
                    }
                };


            xhr.send(
                formData
            );
        }
    }


    /* =========================================
       NORMAL FILE UPLOAD PROGRESS
       Gallery etc.
    ========================================= */

    document
        .querySelectorAll(
            "[data-upload-form]"
        )
        .forEach((form) => {

            /*
             * Book and Bayan already have
             * their own upload handlers.
             */

            if (
                form.hasAttribute(
                    "data-book-form"
                ) ||
                form.hasAttribute(
                    "data-bayan-form"
                )
            ) {
                return;
            }


            form.addEventListener(
                "submit",
                (event) => {

                    const input =
                        form.querySelector(
                            "[data-upload-input]"
                        );


                    if (
                        !input ||
                        !input.files ||
                        !input.files.length
                    ) {
                        return;
                    }


                    event.preventDefault();


                    const progress =
                        form.querySelector(
                            "[data-upload-progress]"
                        );

                    const bar =
                        form.querySelector(
                            "[data-upload-bar]"
                        );

                    const percent =
                        form.querySelector(
                            "[data-upload-percent]"
                        );

                    const status =
                        form.querySelector(
                            "[data-upload-status]"
                        );

                    const submit =
                        form.querySelector(
                            "[data-submit-button]"
                        );


                    if (progress) {
                        progress.hidden = false;
                    }

                    if (submit) {
                        submit.disabled = true;
                    }


                    const xhr =
                        new XMLHttpRequest();


                    xhr.open(
                        "POST",
                        form.action ||
                        window.location.href,
                        true
                    );


                    xhr.setRequestHeader(
                        "X-Requested-With",
                        "XMLHttpRequest"
                    );


                    xhr.setRequestHeader(
                        "Accept",
                        "application/json"
                    );


                    setCsrfHeader(
                        xhr,
                        form
                    );


                    const formData =
                        new FormData(form);


                    xhr.upload.onprogress =
                        (event) => {

                            if (
                                !event.lengthComputable
                            ) {
                                return;
                            }


                            const value =
                                Math.round(
                                    (
                                        event.loaded /
                                        event.total
                                    ) *
                                    100
                                );


                            if (bar) {
                                bar.style.width =
                                    `${value}%`;
                            }


                            if (percent) {
                                percent.textContent =
                                    `${value}%`;
                            }


                            if (status) {

                                status.textContent =
                                    value >= 100
                                        ? "Processing..."
                                        : "Uploading...";
                            }
                        };


                    xhr.onload =
                        () => {

                            let data = null;


                            try {

                                data =
                                    JSON.parse(
                                        xhr.responseText
                                    );

                            } catch (error) {

                                data = null;
                            }


                            if (
                                xhr.status >= 200 &&
                                xhr.status < 300 &&
                                data &&
                                data.success
                            ) {

                                const redirect =
                                    getSafeRedirect(
                                        data.redirect
                                    );


                                if (redirect) {

                                    window.location.href =
                                        redirect;

                                    return;
                                }


                                window.location.reload();

                                return;
                            }


                            if (submit) {
                                submit.disabled = false;
                            }


                            const message =
                                data &&
                                data.message
                                    ? data.message
                                    : "Upload failed.";


                            alert(message);
                        };


                    xhr.onerror =
                        () => {

                            if (submit) {
                                submit.disabled = false;
                            }


                            if (status) {

                                status.textContent =
                                    "Upload failed. Please check your connection.";
                            }
                        };


                    xhr.send(
                        formData
                    );
                }
            );
        });

});