from datetime import datetime
from html.parser import HTMLParser
from ipaddress import ip_address
from urllib.parse import (
    parse_qs,
    urlencode,
    urljoin,
    urlparse,
)
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)
import json
import socket

from argon2 import PasswordHasher

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from extensions import db

from models import (
    Admin,
    Article,
    Bayan,
    Book,
    Adab,
    GalleryItem,
    ContactMessage,
)

from services.media import (
    upload_file,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
)


admin_bp = Blueprint(
    "admin",
    __name__,
)

hasher = PasswordHasher()


# =========================================================
# SECURITY CONSTANTS
# =========================================================

MAX_METADATA_URL_LENGTH = 2048
MAX_METADATA_HTML_SIZE = 2 * 1024 * 1024
MAX_OEMBED_RESPONSE_SIZE = 512 * 1024

MAX_REDIRECTS = 3
NETWORK_TIMEOUT = 8

ALLOWED_PLATFORMS = {
    "YouTube",
    "Facebook",
    "Instagram",
    "Other",
}


# =========================================================
# HELPERS
# =========================================================

def _save(file, folder, allowed):
    return upload_file(
        file,
        folder,
        current_app.config["UPLOAD_FOLDER"],
        current_app.config,
        allowed,
    )


def _is_ajax():
    """
    Detect AJAX / JSON requests.

    Normal browser request:
        flash + render/redirect

    AJAX request:
        JSON response
    """

    return (
        request.headers.get(
            "X-Requested-With",
            "",
        ).lower()
        == "xmlhttprequest"
        or "application/json"
        in request.headers.get(
            "Accept",
            "",
        ).lower()
    )


def _ajax_success(
    message,
    endpoint,
):
    return jsonify(
        {
            "success": True,
            "message": message,
            "redirect": url_for(endpoint),
        }
    )


def _ajax_error(
    message,
    status=400,
):
    return (
        jsonify(
            {
                "success": False,
                "message": message,
            }
        ),
        status,
    )


def _render_or_json_error(
    template,
    message,
    status=400,
):
    """
    Validation helper.

    Normal request:
        flash + render form

    AJAX request:
        JSON error
    """

    if _is_ajax():
        return _ajax_error(
            message,
            status,
        )

    flash(
        message,
        "error",
    )

    return (
        render_template(template),
        status,
    )


# =========================================================
# METADATA PARSER
# =========================================================

class MetaParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.meta = {}
        self._title_parts = []
        self.in_title = False

    def handle_starttag(
        self,
        tag,
        attrs,
    ):
        attrs = dict(attrs)

        if tag.lower() == "meta":

            key = (
                attrs.get("property")
                or attrs.get("name")
                or ""
            ).strip().lower()

            content = attrs.get(
                "content"
            )

            if key and content:
                self.meta[key] = content.strip()

        elif tag.lower() == "title":

            self.in_title = True

    def handle_endtag(
        self,
        tag,
    ):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(
        self,
        data,
    ):
        if self.in_title:

            cleaned = data.strip()

            if cleaned:
                self._title_parts.append(
                    cleaned
                )

    @property
    def title(self):
        return " ".join(
            self._title_parts
        ).strip()


# =========================================================
# TEXT LIMIT
# =========================================================

def _limit_text(
    text,
    limit,
):
    if not text:
        return ""

    text = " ".join(
        text.split()
    )

    if len(text) <= limit:
        return text

    shortened = text[:limit].rsplit(
        " ",
        1,
    )[0]

    if not shortened:
        shortened = text[:limit]

    return (
        shortened.rstrip(
            ".,!?;:"
        )
        + "..."
    )


# =========================================================
# URL HELPERS
# =========================================================

def _normalise_host(host):
    """
    Normalize a hostname for domain comparisons.
    """

    host = (
        host or ""
    ).lower().strip()

    host = host.rstrip(".")

    if host.startswith("www."):
        host = host[4:]

    return host


def _host_matches(
    host,
    domains,
):
    """
    Safely check whether a hostname belongs to one
    of the allowed domains.

    Example:
        youtube.com
        www.youtube.com
        m.youtube.com

    are accepted for youtube.com.
    """

    host = _normalise_host(
        host
    )

    if not host:
        return False

    for domain in domains:

        domain = _normalise_host(
            domain
        )

        if (
            host == domain
            or host.endswith(
                "." + domain
            )
        ):
            return True

    return False


def _is_private_host(
    hostname,
):
    """
    Return True when the hostname resolves to a
    private/local/non-public address.

    Both IPv4 and IPv6 are checked.

    DNS failures are rejected.

    This function fails closed.
    """

    if not hostname:
        return True

    hostname = hostname.strip().lower()
    hostname = hostname.rstrip(".")

    if not hostname:
        return True

    # -----------------------------------------------------
    # Local hostnames
    # -----------------------------------------------------

    if hostname in {
        "localhost",
        "localhost.localdomain",
        "local",
    }:
        return True

    # -----------------------------------------------------
    # Direct IP address
    # -----------------------------------------------------

    try:

        address = ip_address(
            hostname
        )

        return (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
            or not address.is_global
        )

    except ValueError:
        pass

    # -----------------------------------------------------
    # DNS resolution
    # -----------------------------------------------------

    try:

        results = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )

    except (
        socket.gaierror,
        socket.herror,
        socket.timeout,
        OSError,
    ):
        # Fail closed.
        return True

    if not results:
        return True

    addresses = set()

    for result in results:

        sockaddr = result[4]

        if not sockaddr:
            continue

        resolved_address = sockaddr[0]

        try:

            address = ip_address(
                resolved_address
            )

        except ValueError:
            return True

        addresses.add(
            address
        )

    if not addresses:
        return True

    # Every resolved address must be public.
    for address in addresses:

        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
            or not address.is_global
        ):
            return True

    return False


def _validate_external_url(
    url,
):
    """
    Validate an external HTTP/HTTPS URL before
    any server-side request is made.

    Protection includes:

    - HTTP/HTTPS only
    - maximum URL length
    - no embedded username/password
    - valid hostname
    - no private/local IP
    - no loopback
    - no link-local
    - no reserved/multicast/unspecified IP
    - DNS failure rejected
    - only standard HTTP/HTTPS ports
    """

    if not isinstance(
        url,
        str,
    ):
        raise ValueError(
            "Please enter a valid video URL."
        )

    url = url.strip()

    if not url:
        raise ValueError(
            "Please enter a valid video URL."
        )

    if len(url) > MAX_METADATA_URL_LENGTH:
        raise ValueError(
            "The video URL is too long."
        )

    # Reject control characters.
    if any(
        ord(char) < 32
        or ord(char) == 127
        for char in url
    ):
        raise ValueError(
            "The video URL contains invalid characters."
        )

    try:

        parsed = urlparse(
            url
        )

    except ValueError:

        raise ValueError(
            "Please enter a valid video URL."
        )

    scheme = parsed.scheme.lower()

    if scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Please enter a valid HTTP or HTTPS URL."
        )

    if not parsed.netloc:
        raise ValueError(
            "Please enter a valid video URL."
        )

    # -----------------------------------------------------
    # Reject credentials
    # -----------------------------------------------------

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "URLs containing login credentials are not allowed."
        )

    # -----------------------------------------------------
    # Hostname
    # -----------------------------------------------------

    hostname = parsed.hostname

    if not hostname:
        raise ValueError(
            "Please enter a valid video URL."
        )

    hostname = hostname.strip()

    if not hostname:
        raise ValueError(
            "Please enter a valid video URL."
        )

    # -----------------------------------------------------
    # Port
    # -----------------------------------------------------

    try:

        port = parsed.port

    except ValueError:

        raise ValueError(
            "Please enter a valid URL port."
        )

    allowed_port = (
        80
        if scheme == "http"
        else 443
    )

    if (
        port is not None
        and port != allowed_port
    ):
        raise ValueError(
            "Only standard HTTP/HTTPS ports are allowed."
        )

    # -----------------------------------------------------
    # Public IP validation
    # -----------------------------------------------------

    if _is_private_host(
        hostname
    ):
        raise ValueError(
            "This URL cannot be accessed."
        )

    return parsed


def _validate_thumbnail_url(
    url,
):
    """
    Validate an externally stored thumbnail URL.

    HTTPS is preferred/required for stored thumbnails
    to avoid mixed-content problems.
    """

    if not url:
        return ""

    parsed = _validate_external_url(
        url
    )

    if parsed.scheme.lower() != "https":
        return ""

    return parsed.geturl()


# =========================================================
# SAFE REDIRECT HANDLER
# =========================================================

class _NoRedirectHandler(
    HTTPRedirectHandler
):
    """
    Prevent urllib from automatically following redirects.

    Redirects are manually processed so every destination
    can be validated before another request is made.
    """

    def redirect_request(
        self,
        req,
        fp,
        code,
        msg,
        headers,
        newurl,
    ):
        return None


SAFE_HTTP_OPENER = build_opener(
    _NoRedirectHandler()
)


def _open_safe_url(
    url,
    headers=None,
):
    """
    Open an external URL safely.

    Every redirect is validated.

    Maximum redirects:
        MAX_REDIRECTS

    Every redirect destination must pass:
        _validate_external_url()
    """

    current_url = url

    for _ in range(
        MAX_REDIRECTS + 1
    ):

        _validate_external_url(
            current_url
        )

        request_obj = Request(
            current_url,
            headers=headers or {},
        )

        try:

            response = SAFE_HTTP_OPENER.open(
                request_obj,
                timeout=NETWORK_TIMEOUT,
            )

        except Exception as exc:

            code = getattr(
                exc,
                "code",
                None,
            )

            # Because automatic redirects are disabled,
            # urllib raises HTTPError for redirects.
            if code not in {
                301,
                302,
                303,
                307,
                308,
            }:
                raise

            location = None

            try:

                location = exc.headers.get(
                    "Location"
                )

            except Exception:

                location = None

            if not location:
                raise ValueError(
                    "The external URL returned an invalid redirect."
                )

            next_url = urljoin(
                current_url,
                location,
            )

            # Validate the redirect destination
            # before following it.
            _validate_external_url(
                next_url
            )

            current_url = next_url

            continue

        return response

    raise ValueError(
        "Too many redirects."
    )


def _read_limited_response(
    response,
    max_bytes,
):
    """
    Read max_bytes + 1 bytes.

    This prevents oversized responses from being
    silently loaded into memory.
    """

    content_length = response.headers.get(
        "Content-Length"
    )

    if content_length:

        try:

            if int(content_length) > max_bytes:
                raise ValueError(
                    "The external response is too large."
                )

        except ValueError as exc:

            if str(exc) == (
                "The external response is too large."
            ):
                raise

    data = response.read(
        max_bytes + 1
    )

    if len(data) > max_bytes:
        raise ValueError(
            "The external response is too large."
        )

    return data


# =========================================================
# YOUTUBE VIDEO ID
# =========================================================

def _youtube_video_id(
    url,
):
    parsed = urlparse(
        url
    )

    host = _normalise_host(
        parsed.hostname
    )

    if host == "youtu.be":

        value = (
            parsed.path
            .strip("/")
            .split("/")
        )

        if value:
            return value[0]

        return None

    if host in {
        "youtube.com",
        "m.youtube.com",
    }:

        query = parse_qs(
            parsed.query
        )

        if query.get("v"):
            return query["v"][0]

        parts = (
            parsed.path
            .strip("/")
            .split("/")
        )

        if (
            len(parts) >= 2
            and parts[0].lower()
            in {
                "shorts",
                "embed",
                "live",
            }
        ):
            return parts[1]

    return None


# =========================================================
# FETCH PAGE HTML
# =========================================================

def _fetch_page_html(
    url,
):
    """
    Fetch page HTML safely.

    Redirects are validated.
    Response size is limited.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "*/*;q=0.8"
        ),
        "Accept-Language": (
            "en-US,en;q=0.9"
        ),
    }

    with _open_safe_url(
        url,
        headers=headers,
    ) as response:

        content_type = (
            response.headers.get(
                "Content-Type",
                "",
            ).lower()
        )

        if (
            content_type
            and not any(
                value in content_type
                for value in {
                    "text/html",
                    "application/xhtml+xml",
                    "application/xml",
                }
            )
        ):
            return ""

        content = _read_limited_response(
            response,
            MAX_METADATA_HTML_SIZE,
        )

        return content.decode(
            "utf-8",
            errors="ignore",
        )


# =========================================================
# SOCIAL VIDEO METADATA
# =========================================================

def _fetch_metadata(
    url,
    platform,
):
    """
    Fetch metadata for a social/video URL.

    Known platforms are restricted to their own domains.
    """

    parsed = _validate_external_url(
        url
    )

    host = _normalise_host(
        parsed.hostname
    )

    platform = (
        platform or "Other"
    ).strip()

    if platform not in ALLOWED_PLATFORMS:
        platform = "Other"

    platform_domains = {
        "YouTube": (
            "youtube.com",
            "youtu.be",
        ),
        "Facebook": (
            "facebook.com",
            "fb.watch",
        ),
        "Instagram": (
            "instagram.com",
        ),
    }

    # -----------------------------------------------------
    # Platform/domain validation
    # -----------------------------------------------------

    if platform in platform_domains:

        if not _host_matches(
            host,
            platform_domains[
                platform
            ],
        ):
            raise ValueError(
                f"The URL does not match {platform}."
            )

    metadata = {
        "title": "",
        "description": "",
        "thumbnail": "",
    }

    video_id = _youtube_video_id(
        url
    )

    # =====================================================
    # YOUTUBE THUMBNAIL
    # =====================================================

    if (
        platform == "YouTube"
        and video_id
    ):

        metadata["thumbnail"] = (
            "https://i.ytimg.com/vi/"
            f"{video_id}/hqdefault.jpg"
        )

    # =====================================================
    # YOUTUBE OEMBED
    # =====================================================

    if (
        platform == "YouTube"
        and video_id
    ):

        try:

            oembed_url = (
                "https://www.youtube.com/oembed?"
                + urlencode(
                    {
                        "url": url,
                        "format": "json",
                    }
                )
            )

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                ),
                "Accept": (
                    "application/json"
                ),
            }

            with _open_safe_url(
                oembed_url,
                headers=headers,
            ) as response:

                data = json.loads(
                    _read_limited_response(
                        response,
                        MAX_OEMBED_RESPONSE_SIZE,
                    ).decode(
                        "utf-8",
                        errors="ignore",
                    )
                )

            metadata["title"] = str(
                data.get(
                    "title",
                    "",
                )
            ).strip()

        except Exception:
            pass

    # =====================================================
    # OPEN GRAPH / PAGE METADATA
    # =====================================================

    try:

        html = _fetch_page_html(
            url
        )

        if html:

            parser = MetaParser()

            parser.feed(
                html
            )

            metadata["title"] = (
                metadata["title"]
                or parser.meta.get(
                    "og:title",
                    "",
                )
                or parser.meta.get(
                    "twitter:title",
                    "",
                )
                or parser.title
            )

            metadata["description"] = (
                parser.meta.get(
                    "og:description",
                    "",
                )
                or parser.meta.get(
                    "description",
                    "",
                )
                or parser.meta.get(
                    "twitter:description",
                    "",
                )
            )

            thumbnail = (
                metadata["thumbnail"]
                or parser.meta.get(
                    "og:image",
                    "",
                )
                or parser.meta.get(
                    "twitter:image",
                    "",
                )
            )

            if thumbnail:

                try:

                    metadata["thumbnail"] = (
                        _validate_thumbnail_url(
                            thumbnail
                        )
                    )

                except ValueError:

                    metadata["thumbnail"] = ""

    except Exception:
        pass

    # =====================================================
    # LIMIT METADATA
    # =====================================================

    metadata["title"] = _limit_text(
        metadata["title"],
        100,
    )

    metadata["description"] = _limit_text(
        metadata["description"],
        500,
    )

    if not metadata["title"]:
        metadata["title"] = "Bayan"

    return metadata


# =========================================================
# LOGIN
# =========================================================

@admin_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        user = Admin.query.filter_by(
            username=username
        ).first()

        if user:

            try:

                if hasher.verify(
                    user.password_hash,
                    password,
                ):

                    login_user(
                        user
                    )

                    return redirect(
                        url_for(
                            "admin.dashboard"
                        )
                    )

            except Exception:
                pass

        flash(
            "Invalid username or password.",
            "error",
        )

    return render_template(
        "admin/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@admin_bp.route(
    "/logout"
)
@login_required
def logout():

    logout_user()

    return redirect(
        url_for(
            "admin.login"
        )
    )


# =========================================================
# DASHBOARD
# =========================================================

@admin_bp.route("/")
@login_required
def dashboard():

    return render_template(
        "admin/dashboard.html",
        counts={
            "articles": Article.query.count(),
            "bayans": Bayan.query.count(),
            "books": Book.query.count(),
            "adab": Adab.query.count(),
            "gallery": GalleryItem.query.count(),
            "messages": ContactMessage.query.count(),
        },
    )


# =========================================================
# ARTICLES
# =========================================================

@admin_bp.route(
    "/articles"
)
@login_required
def articles():

    return render_template(
        "admin/articles.html",
        items=(
            Article.query
            .order_by(
                Article.created_at.desc()
            )
            .all()
        ),
    )


@admin_bp.route(
    "/articles/new",
    methods=["GET", "POST"],
)
@login_required
def article_new():

    if request.method == "POST":

        title = request.form.get(
            "title",
            "",
        ).strip()

        summary = request.form.get(
            "summary",
            "",
        ).strip()

        content = request.form.get(
            "content",
            "",
        ).strip()

        is_published = bool(
            request.form.get(
                "is_published"
            )
        )

        if not title:

            return _render_or_json_error(
                "admin/article_form.html",
                "Title is required.",
            )

        if len(title) > 120:

            return _render_or_json_error(
                "admin/article_form.html",
                "Title must be 120 characters or less.",
            )

        if len(summary) > 300:

            return _render_or_json_error(
                "admin/article_form.html",
                "Short summary must be 300 characters or less.",
            )

        if not content:

            return _render_or_json_error(
                "admin/article_form.html",
                "Article content is required.",
            )

        try:

            item = Article(
                title=title,
                summary=summary,
                content=content,
                is_published=is_published,
            )

            db.session.add(
                item
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            return _render_or_json_error(
                "admin/article_form.html",
                "Article could not be saved.",
                500,
            )

        if _is_ajax():

            return _ajax_success(
                "Article created successfully.",
                "admin.articles",
            )

        flash(
            "Article created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin.articles"
            )
        )

    return render_template(
        "admin/article_form.html",
        item=None,
    )


@admin_bp.route(
    "/articles/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def article_delete(
    item_id,
):

    item = (
        db.session.get(
            Article,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Article deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.articles"
        )
    )


# =========================================================
# BOOKS
# =========================================================

# =========================================================
# BOOKS
# =========================================================

@admin_bp.route("/books")
@login_required
def books():

    return render_template(
        "admin/books.html",
        items=(
            Book.query
            .order_by(
                Book.created_at.desc()
            )
            .all()
        ),
    )


@admin_bp.route(
    "/books/new",
    methods=["GET", "POST"],
)
@login_required
def book_new():

    if request.method == "POST":

        book_type = request.form.get(
            "book_type",
            "read",
        ).strip()

        if book_type not in {
            "read",
            "order",
        }:
            book_type = "read"

        title = request.form.get(
            "title",
            "",
        ).strip()

        author = request.form.get(
            "author",
            "Shahid Nomani",
        ).strip()

        if not title:
            return _render_or_json_error(
                "admin/book_form.html",
                "Title is required.",
            )

        if len(title) > 150:
            return _render_or_json_error(
                "admin/book_form.html",
                "Title must be 150 characters or less.",
            )

        if not author:
            return _render_or_json_error(
                "admin/book_form.html",
                "Author is required.",
            )

        if len(author) > 150:
            return _render_or_json_error(
                "admin/book_form.html",
                "Author must be 150 characters or less.",
            )

        image = request.files.get(
            "image"
        )

        if (
            not image
            or not image.filename
        ):
            return _render_or_json_error(
                "admin/book_form.html",
                "Cover image is required.",
            )

        # =================================================
        # READ ONLINE
        # =================================================

        if book_type == "read":

            pdf = request.files.get(
                "pdf"
            )

            if (
                not pdf
                or not pdf.filename
            ):
                return _render_or_json_error(
                    "admin/book_form.html",
                    "PDF is required for Read Online books.",
                )

            try:

                item = Book(
                    title=title,
                    author=author,
                    description="",
                    book_type="read",
                    buy_link="",
                    price=None,
                    is_published=bool(
                        request.form.get(
                            "is_published"
                        )
                    ),
                )

                item.image = _save(
                    image,
                    "books",
                    IMAGE_EXTENSIONS,
                )

                item.pdf = _save(
                    pdf,
                    "books",
                    {"pdf"},
                )

                if not item.pdf:
                    raise ValueError(
                        "PDF upload returned an empty path."
                    )

            except Exception:

                db.session.rollback()

                return _render_or_json_error(
                    "admin/book_form.html",
                    "Book files could not be saved.",
                    500,
                )

        # =================================================
        # SELL / DELIVERY
        # =================================================

        else:

            price_text = request.form.get(
                "price",
                "",
            ).strip()

            if not price_text:
                return _render_or_json_error(
                    "admin/book_form.html",
                    "Price is required for Sell / Delivery books.",
                )

            try:

                price = int(
                    price_text
                )

            except ValueError:

                return _render_or_json_error(
                    "admin/book_form.html",
                    "Please enter a valid price.",
                )

            if price < 0:
                return _render_or_json_error(
                    "admin/book_form.html",
                    "Price cannot be negative.",
                )

            try:

                item = Book(
                    title=title,
                    author=author,
                    description="",
                    book_type="order",
                    buy_link="",
                    price=price,
                    is_published=bool(
                        request.form.get(
                            "is_published"
                        )
                    ),
                    pdf=None,
                )

                item.image = _save(
                    image,
                    "books",
                    IMAGE_EXTENSIONS,
                )

            except Exception:

                db.session.rollback()

                return _render_or_json_error(
                    "admin/book_form.html",
                    "Book cover could not be saved.",
                    500,
                )

        # =================================================
        # SAVE BOOK
        # =================================================

        db.session.add(
            item
        )

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            return _render_or_json_error(
                "admin/book_form.html",
                "Book could not be saved.",
                500,
            )

        if _is_ajax():

            return _ajax_success(
                "Book uploaded successfully!",
                "admin.books",
            )

        flash(
            "Book uploaded successfully!",
            "success",
        )

        return redirect(
            url_for(
                "admin.books"
            )
        )

    return render_template(
        "admin/book_form.html",
        item=None,
    )


@admin_bp.route(
    "/books/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def book_delete(
    item_id,
):

    item = (
        db.session.get(
            Book,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Book deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.books"
        )
    )

# =========================================================
# BAYANS
# =========================================================

@admin_bp.route(
    "/bayans"
)
@login_required
def bayans():

    return render_template(
        "admin/bayans.html",
        items=(
            Bayan.query
            .order_by(
                Bayan.created_at.desc()
            )
            .all()
        ),
    )


# =========================================================
# BAYAN METADATA PREVIEW
# =========================================================

@admin_bp.route(
    "/bayans/preview",
    methods=["POST"],
)
@login_required
def bayan_preview():

    data = request.get_json(
        silent=True
    ) or {}

    url = data.get(
        "url",
        "",
    )

    platform = data.get(
        "platform",
        "Other",
    )

    if not isinstance(
        url,
        str,
    ):

        return _ajax_error(
            "Enter a valid video URL."
        )

    if not isinstance(
        platform,
        str,
    ):

        platform = "Other"

    url = url.strip()
    platform = platform.strip()

    if not url:

        return _ajax_error(
            "Enter a video URL."
        )

    if platform not in ALLOWED_PLATFORMS:

        platform = "Other"

    try:

        metadata = _fetch_metadata(
            url,
            platform,
        )

        return jsonify(
            {
                "success": True,
                **metadata,
            }
        )

    except ValueError as exc:

        return _ajax_error(
            str(exc)
        )

    except Exception:

        return _ajax_error(
            "Video details could not be loaded."
        )


# =========================================================
# ADD BAYAN
# =========================================================

@admin_bp.route(
    "/bayans/new",
    methods=["GET", "POST"],
)
@login_required
def bayan_new():

    if request.method == "POST":

        upload_type = request.form.get(
            "upload_type",
            "online",
        ).strip()

        is_published = bool(
            request.form.get(
                "is_published"
            )
        )

        if upload_type not in {
            "online",
            "upload",
        }:

            upload_type = "online"

        # =================================================
        # ONLINE BAYAN
        # =================================================

        if upload_type == "online":

            title = request.form.get(
                "title",
                "",
            ).strip()

            platform = request.form.get(
                "platform",
                "Other",
            ).strip()

            video_url = request.form.get(
                "video_url",
                "",
            ).strip()

            thumbnail = request.form.get(
                "thumbnail",
                "",
            ).strip()

            if not title:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Title is required.",
                )

            if len(title) > 35:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Title must be 35 characters or less.",
                )

            if not video_url:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Video URL is required.",
                )

            if platform not in ALLOWED_PLATFORMS:

                platform = "Other"

            try:

                metadata = _fetch_metadata(
                    video_url,
                    platform,
                )

            except ValueError as exc:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    str(exc),
                )

            except Exception:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "The video URL could not be verified.",
                )

            thumbnail = (
                thumbnail
                or metadata.get(
                    "thumbnail",
                    "",
                )
            )

            # Validate manually supplied or fetched
            # thumbnail before storing it.
            if thumbnail:

                try:

                    thumbnail = (
                        _validate_thumbnail_url(
                            thumbnail
                        )
                    )

                except ValueError:

                    thumbnail = ""

            item = Bayan(
                title=title,
                description="",
                upload_type="online",
                video_url=video_url,
                platform=platform,
                thumbnail=thumbnail,
                video_file=None,
                is_published=is_published,
            )

        # =================================================
        # OFFLINE BAYAN
        # =================================================

        else:

            title = request.form.get(
                "offline_title",
                "",
            ).strip()

            video = request.files.get(
                "video_file"
            )

            thumb = request.files.get(
                "thumbnail_file"
            )

            if not title:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Title is required.",
                )

            if len(title) > 35:

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Title must be 35 characters or less.",
                )

            if (
                not video
                or not video.filename
            ):

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Video file is required.",
                )

            try:

                item = Bayan(
                    title=title,
                    description="",
                    upload_type="upload",
                    platform="",
                    video_url="",
                    thumbnail=None,
                    video_file=None,
                    is_published=is_published,
                )

                item.video_file = _save(
                    video,
                    "bayans",
                    VIDEO_EXTENSIONS,
                )

                if (
                    thumb
                    and thumb.filename
                ):

                    item.thumbnail = _save(
                        thumb,
                        "bayans",
                        IMAGE_EXTENSIONS,
                    )

            except Exception:

                db.session.rollback()

                return _render_or_json_error(
                    "admin/bayan_form.html",
                    "Bayan video could not be saved.",
                    500,
                )

        try:

            db.session.add(
                item
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            return _render_or_json_error(
                "admin/bayan_form.html",
                "Bayan could not be saved.",
                500,
            )

        if _is_ajax():

            return _ajax_success(
                "Bayan created successfully.",
                "admin.bayans",
            )

        flash(
            "Bayan created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin.bayans"
            )
        )

    return render_template(
        "admin/bayan_form.html"
    )


@admin_bp.route(
    "/bayans/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def bayan_delete(
    item_id,
):

    item = (
        db.session.get(
            Bayan,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Bayan deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.bayans"
        )
    )


# =========================================================
# URDU ADAB
# =========================================================

@admin_bp.route(
    "/adab"
)
@login_required
def adab():

    return render_template(
        "admin/adab.html",
        items=(
            Adab.query
            .order_by(
                Adab.created_at.desc()
            )
            .all()
        ),
    )


@admin_bp.route(
    "/adab/new",
    methods=["GET", "POST"],
)
@login_required
def adab_new():

    if request.method == "POST":

        category = request.form.get(
            "category",
            "Other",
        ).strip()

        title = request.form.get(
            "title",
            "",
        ).strip()

        allowed_categories = {
            "Shayari",
            "Ghazal",
            "Poetry",
            "Thought",
            "Other",
        }

        if category not in allowed_categories:
            category = "Other"

        if not title:

            return _render_or_json_error(
                "admin/adab_form.html",
                "Title is required.",
            )

        if len(title) > 150:

            return _render_or_json_error(
                "admin/adab_form.html",
                "Title must be 150 characters or less.",
            )

        item = Adab(
            category=category,
            title=title,
            summary="",
            content="",
            image=None,
            pdf=None,
            is_published=bool(
                request.form.get(
                    "is_published"
                )
            ),
        )

        try:

            db.session.add(
                item
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            return _render_or_json_error(
                "admin/adab_form.html",
                "Adab item could not be saved.",
                500,
            )

        flash(
            "Adab item created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin.adab"
            )
        )

    return render_template(
        "admin/adab_form.html",
        item=None,
    )


@admin_bp.route(
    "/adab/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def adab_delete(
    item_id,
):

    item = (
        db.session.get(
            Adab,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Item deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.adab"
        )
    )


# =========================================================
# GALLERY
# =========================================================

@admin_bp.route(
    "/gallery"
)
@login_required
def gallery():

    return render_template(
        "admin/gallery.html",
        items=(
            GalleryItem.query
            .order_by(
                GalleryItem.created_at.desc()
            )
            .all()
        ),
    )


@admin_bp.route(
    "/gallery/new",
    methods=["GET", "POST"],
)
@login_required
def gallery_new():

    if request.method == "POST":

        image = request.files.get(
            "image"
        )

        if (
            not image
            or not image.filename
        ):

            return _render_or_json_error(
                "admin/gallery_form.html",
                "Image is required.",
            )

        caption = request.form.get(
            "caption",
            "",
        ).strip()

        if len(caption) > 300:

            return _render_or_json_error(
                "admin/gallery_form.html",
                "Caption must be 300 characters or less.",
            )

        try:

            value = _save(
                image,
                "gallery",
                IMAGE_EXTENSIONS,
            )

            item = GalleryItem(
                image=value,
                caption=caption,
                is_published=bool(
                    request.form.get(
                        "is_published"
                    )
                ),
            )

            db.session.add(
                item
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            return _render_or_json_error(
                "admin/gallery_form.html",
                "Gallery photo could not be saved.",
                500,
            )

        flash(
            "Gallery photo added.",
            "success",
        )

        return redirect(
            url_for(
                "admin.gallery"
            )
        )

    return render_template(
        "admin/gallery_form.html",
        item=None,
    )


@admin_bp.route(
    "/gallery/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def gallery_delete(
    item_id,
):

    item = (
        db.session.get(
            GalleryItem,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Photo deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.gallery"
        )
    )


# =========================================================
# MESSAGES
# =========================================================

@admin_bp.route(
    "/messages"
)
@login_required
def messages():

    return render_template(
        "admin/messages.html",
        items=(
            ContactMessage.query
            .order_by(
                ContactMessage.created_at.desc()
            )
            .all()
        ),
    )


@admin_bp.route(
    "/messages/<int:item_id>/reply",
    methods=["POST"],
)
@login_required
def message_reply(
    item_id,
):

    item = (
        db.session.get(
            ContactMessage,
            item_id,
        )
        or abort(404)
    )

    reply = request.form.get(
        "reply",
        "",
    ).strip()

    if len(reply) > 5000:

        flash(
            "Reply is too long.",
            "error",
        )

        return redirect(
            url_for(
                "admin.messages"
            )
        )

    item.reply = reply
    item.status = "Replied"
    item.replied_at = datetime.utcnow()

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Reply could not be saved.",
            "error",
        )

        return redirect(
            url_for(
                "admin.messages"
            )
        )

    flash(
        "Reply saved.",
        "success",
    )

    return redirect(
        url_for(
            "admin.messages"
        )
    )


@admin_bp.route(
    "/messages/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def message_delete(
    item_id,
):

    item = (
        db.session.get(
            ContactMessage,
            item_id,
        )
        or abort(404)
    )

    db.session.delete(
        item
    )

    db.session.commit()

    flash(
        "Message deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin.messages"
        )
    )