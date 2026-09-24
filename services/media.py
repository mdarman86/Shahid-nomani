import os
import uuid
from pathlib import Path

from flask import url_for
from werkzeug.utils import secure_filename


try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
}

VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov",
    "ogg",
}

DOCUMENT_EXTENSIONS = {
    "pdf",
}


# =========================================================
# ALL APPLICATION-SAFE EXTENSIONS
# =========================================================

SAFE_EXTENSIONS = (
    IMAGE_EXTENSIONS
    | VIDEO_EXTENSIONS
    | DOCUMENT_EXTENSIONS
)


# =========================================================
# FILE SIZE LIMITS
# =========================================================

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024


# =========================================================
# HELPERS
# =========================================================

def _extension(filename):
    filename = filename or ""

    if "." not in filename:
        return ""

    return (
        filename
        .rsplit(".", 1)[1]
        .lower()
        .strip()
    )


def _normalise_allowed(allowed):
    """
    Normalise the extensions supplied by a route.

    IMPORTANT:
    The route is NOT allowed to introduce a new
    dangerous extension such as .exe.

    Only extensions already defined by the application
    are accepted.
    """

    if allowed is None:
        return set(SAFE_EXTENSIONS)

    normalised = {
        str(item)
        .lower()
        .lstrip(".")
        .strip()
        for item in allowed
    }

    unsafe = normalised - SAFE_EXTENSIONS

    if unsafe:
        raise ValueError(
            "One or more requested file types are not allowed."
        )

    return normalised


def _is_production(config):
    """
    Read the centralized production setting from Flask config.

    Local development:
        IS_PRODUCTION = False

    Production:
        IS_PRODUCTION = True
    """

    return bool(
        config.get(
            "IS_PRODUCTION",
            False,
        )
    )

def _max_size_for_extension(ext):
    if ext in IMAGE_EXTENSIONS:
        return MAX_IMAGE_SIZE

    if ext in VIDEO_EXTENSIONS:
        return MAX_VIDEO_SIZE

    if ext in DOCUMENT_EXTENSIONS:
        return MAX_DOCUMENT_SIZE

    return 0


def _read_file_bytes(file, size):
    """
    Read a limited amount of data while restoring
    the original file position afterwards.
    """

    try:
        current_position = file.tell()

    except (AttributeError, OSError):
        current_position = 0

    try:
        file.seek(0)

        data = file.read(size)

    finally:
        try:
            file.seek(current_position)

        except (AttributeError, OSError):
            pass

    return data


def _file_size(file):
    """
    Return file size without permanently changing
    the current file position.
    """

    try:
        current_position = file.tell()

    except (AttributeError, OSError):
        current_position = 0

    try:
        file.seek(0, 2)

        size = file.tell()

    except (AttributeError, OSError):

        size = 0

    finally:
        try:
            file.seek(current_position)

        except (AttributeError, OSError):
            pass

    return size


# =========================================================
# FILE SIGNATURE VALIDATION
# =========================================================

def _validate_file_signature(file, ext):
    """
    Verify that file content matches its extension.

    Extension alone is NOT trusted.
    """

    # -----------------------------------------------------
    # JPEG
    # -----------------------------------------------------

    if ext in {"jpg", "jpeg"}:

        header = _read_file_bytes(
            file,
            3,
        )

        if not header.startswith(
            b"\xff\xd8\xff"
        ):
            raise ValueError(
                "The uploaded file is not a valid JPEG image."
            )

        return


    # -----------------------------------------------------
    # PNG
    # -----------------------------------------------------

    if ext == "png":

        header = _read_file_bytes(
            file,
            8,
        )

        if header != b"\x89PNG\r\n\x1a\n":

            raise ValueError(
                "The uploaded file is not a valid PNG image."
            )

        return


    # -----------------------------------------------------
    # GIF
    # -----------------------------------------------------

    if ext == "gif":

        header = _read_file_bytes(
            file,
            6,
        )

        if header not in {
            b"GIF87a",
            b"GIF89a",
        }:

            raise ValueError(
                "The uploaded file is not a valid GIF image."
            )

        return


    # -----------------------------------------------------
    # WEBP
    # -----------------------------------------------------

    if ext == "webp":

        header = _read_file_bytes(
            file,
            12,
        )

        if (
            len(header) < 12
            or header[0:4] != b"RIFF"
            or header[8:12] != b"WEBP"
        ):

            raise ValueError(
                "The uploaded file is not a valid WebP image."
            )

        return


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if ext == "pdf":

        header = _read_file_bytes(
            file,
            5,
        )

        if header != b"%PDF-":

            raise ValueError(
                "The uploaded file is not a valid PDF."
            )

        return


    # -----------------------------------------------------
    # MP4 / MOV
    # -----------------------------------------------------

    if ext in {
        "mp4",
        "mov",
    }:

        header = _read_file_bytes(
            file,
            12,
        )

        if len(header) < 8:

            raise ValueError(
                "The uploaded video file is invalid."
            )

        if header[4:8] != b"ftyp":

            raise ValueError(
                "The uploaded file is not a valid MP4/MOV video."
            )

        return


    # -----------------------------------------------------
    # WEBM
    # -----------------------------------------------------

    if ext == "webm":

        header = _read_file_bytes(
            file,
            4,
        )

        if header != b"\x1a\x45\xdf\xa3":

            raise ValueError(
                "The uploaded file is not a valid WebM video."
            )

        return


    # -----------------------------------------------------
    # OGG
    # -----------------------------------------------------

    if ext == "ogg":

        header = _read_file_bytes(
            file,
            4,
        )

        if header != b"OggS":

            raise ValueError(
                "The uploaded file is not a valid OGG file."
            )

        return


    # -----------------------------------------------------
    # UNKNOWN EXTENSION
    # -----------------------------------------------------

    raise ValueError(
        "This file type is not allowed."
    )


# =========================================================
# UPLOAD FILE
# =========================================================

def upload_file(
    file,
    folder,
    upload_folder,
    config,
    allowed=None,
):
    """
    Secure media upload.

    Production:
        Cloudinary is REQUIRED.

    Local development:
        Cloudinary is preferred.
        Local storage is allowed as fallback.

    Security:
        - Safe extension allowlist
        - File signature validation
        - File size limits
        - Secure filename
        - Production local-storage protection
        - Saved-file verification
    """

    # =====================================================
    # EMPTY FILE
    # =====================================================

    if not file or not file.filename:
        return None


    # =====================================================
    # SAFE FILENAME
    # =====================================================

    filename = secure_filename(
        file.filename
    )

    if not filename:

        raise ValueError(
            "Invalid filename."
        )


    # =====================================================
    # EXTENSION
    # =====================================================

    ext = _extension(
        filename
    )

    if not ext:

        raise ValueError(
            "Uploaded file must have a valid extension."
        )


    # =====================================================
    # SAFE ALLOWLIST
    # =====================================================

    allowed = _normalise_allowed(
        allowed
    )

    if ext not in allowed:

        raise ValueError(
            f"Unsupported file type: .{ext}"
        )


    # =====================================================
    # FILE SIZE
    # =====================================================

    max_size = _max_size_for_extension(
        ext
    )

    if not max_size:

        raise ValueError(
            "This file type is not allowed."
        )


    file_size = _file_size(
        file
    )

    if file_size <= 0:

        raise ValueError(
            "Uploaded file is empty."
        )


    if file_size > max_size:

        max_mb = max_size // (
            1024 * 1024
        )

        raise ValueError(
            "File is too large. "
            f"Maximum allowed size is {max_mb} MB."
        )


    # =====================================================
    # FILE CONTENT VALIDATION
    # =====================================================

    _validate_file_signature(
        file,
        ext,
    )


    # =====================================================
    # CLOUDINARY CONFIG
    # =====================================================

    cloud_name = config.get(
        "CLOUDINARY_CLOUD_NAME"
    )

    api_key = config.get(
        "CLOUDINARY_API_KEY"
    )

    api_secret = config.get(
        "CLOUDINARY_API_SECRET"
    )


    cloudinary_available = bool(
        cloud_name
        and api_key
        and api_secret
        and cloudinary
    )


    # =====================================================
    # CLOUDINARY UPLOAD
    # =====================================================

    if cloudinary_available:

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )


        if ext in IMAGE_EXTENSIONS:

            resource_type = "image"

        elif ext in VIDEO_EXTENSIONS:

            resource_type = "video"

        elif ext in DOCUMENT_EXTENSIONS:

            resource_type = "raw"

        else:

            raise ValueError(
                "Unsupported media type."
            )


        try:

            file.seek(0)

            result = cloudinary.uploader.upload(
                file,
                folder=(
                    f"shahid-nomani/"
                    f"{folder}"
                ),
                resource_type=resource_type,
                unique_filename=True,
                overwrite=False,
            )

        except Exception as exc:

            raise ValueError(
                "Cloudinary upload failed."
            ) from exc


        secure_url = result.get(
            "secure_url"
        )


        if not secure_url:

            raise ValueError(
                "Cloudinary upload failed."
            )


        return secure_url


    # =====================================================
    # PRODUCTION PROTECTION
    # =====================================================

    if _is_production(config):

        raise RuntimeError(
            "Cloudinary storage is required in production. "
            "Local file storage is disabled."
        )


    # =====================================================
    # LOCAL DEVELOPMENT STORAGE
    # =====================================================

    upload_root = Path(
        upload_folder
    ).resolve()


    target_dir = (
        upload_root
        / folder
    ).resolve()


    # Prevent the folder argument from escaping
    # the configured upload directory.

    try:

        target_dir.relative_to(
            upload_root
        )

    except ValueError as exc:

        raise ValueError(
            "Invalid upload folder."
        ) from exc


    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    # =====================================================
    # UNIQUE FILE NAME
    # =====================================================

    unique_name = (
        f"{uuid.uuid4().hex}_"
        f"{filename}"
    )


    destination = (
        target_dir
        / unique_name
    ).resolve()


    # Extra path traversal protection.

    try:

        destination.relative_to(
            target_dir
        )

    except ValueError as exc:

        raise ValueError(
            "Invalid upload destination."
        ) from exc


    # =====================================================
    # SAVE FILE
    # =====================================================

    try:

        file.seek(0)

        file.save(
            destination
        )

    except Exception as exc:

        try:

            if destination.exists():
                destination.unlink()

        except OSError:
            pass

        raise ValueError(
            "File upload failed."
        ) from exc


    # =====================================================
    # VERIFY SAVED FILE
    # =====================================================

    if not destination.exists():

        raise ValueError(
            "File upload failed."
        )


    try:

        saved_size = destination.stat().st_size

    except OSError as exc:

        try:

            destination.unlink()

        except OSError:
            pass

        raise ValueError(
            "Unable to verify uploaded file."
        ) from exc


    if saved_size <= 0:

        try:

            destination.unlink()

        except OSError:
            pass

        raise ValueError(
            "Uploaded file is empty."
        )


    # Saved file must also obey the
    # same maximum size.

    if saved_size > max_size:

        try:

            destination.unlink()

        except OSError:
            pass

        max_mb = max_size // (
            1024 * 1024
        )

        raise ValueError(
            "Uploaded file exceeds the "
            f"maximum allowed size of {max_mb} MB."
        )


    # =====================================================
    # VERIFY SAVED FILE CONTENT
    # =====================================================

    try:

        with open(
            destination,
            "rb",
        ) as saved_file:

            _validate_file_signature(
                saved_file,
                ext,
            )

    except ValueError:

        try:

            destination.unlink()

        except OSError:
            pass

        raise

    except OSError as exc:

        try:

            destination.unlink()

        except OSError:
            pass

        raise ValueError(
            "Unable to verify uploaded file."
        ) from exc


    # =====================================================
    # DATABASE PATH
    # =====================================================

    return (
        Path(folder)
        / unique_name
    ).as_posix()


# =========================================================
# MEDIA URL
# =========================================================

def media_url(
    value,
    folder=None,
):
    """
    Convert stored media value into a usable URL.

    Supports:

        Cloudinary URL
        /static/...
        static/...
        uploads/...
        folder/filename
        filename
    """

    if not value:
        return ""


    value = str(
        value
    ).strip()


    # =====================================================
    # EXTERNAL URL
    # =====================================================

    if value.lower().startswith(
        (
            "http://",
            "https://",
        )
    ):

        return value


    # =====================================================
    # ALREADY AN APPLICATION URL
    # =====================================================

    if value.startswith("/"):

        return value


    # =====================================================
    # REMOVE OLD PREFIX
    # =====================================================

    if value.startswith(
        "static/uploads/"
    ):

        value = value[
            len("static/uploads/"):
        ]


    elif value.startswith(
        "uploads/"
    ):

        value = value[
            len("uploads/"):
        ]


    # =====================================================
    # DATABASE PATH
    # =====================================================

    if (
        "/" in value
        or "\\" in value
    ):

        value = value.replace(
            "\\",
            "/",
        )

        return url_for(
            "static",
            filename=(
                f"uploads/{value}"
            ),
        )


    # =====================================================
    # LEGACY FILENAME
    # =====================================================

    if folder:

        return url_for(
            "static",
            filename=(
                f"uploads/"
                f"{folder}/"
                f"{value}"
            ),
        )


    return url_for(
        "static",
        filename=(
            f"uploads/{value}"
        ),
    )