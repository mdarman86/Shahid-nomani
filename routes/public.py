from pathlib import Path
from urllib.parse import parse_qs, urlparse

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from extensions import db

from models import (
    Article,
    Bayan,
    Book,
    Adab,
    GalleryItem,
    ContactMessage,
)


public_bp = Blueprint(
    "public",
    __name__,
)


# =========================================================
# BOOK TYPES
# =========================================================

ONLINE_BOOK_TYPES = {
    "read",
    "online",
    "read_online",
    "digital",
}

SELL_BOOK_TYPES = {
    "order",
    "sell",
    "buy",
    "delivery",
}


# =========================================================
# YOUTUBE HELPERS
# =========================================================

def _normalise_host(host):

    host = (
        host or ""
    ).lower().strip()

    if host.startswith("www."):

        host = host[4:]

    return host


def _youtube_video_id(url):

    try:

        parsed = urlparse(url)

    except Exception:

        return None


    host = _normalise_host(
        parsed.netloc
    )


    # youtu.be/<id>
    if host == "youtu.be":

        value = (
            parsed.path
            .strip("/")
            .split("/")
        )

        if value and value[0]:

            return value[0]

        return None


    # youtube.com
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
# PDF PATH HELPER
# =========================================================

def _book_pdf_path(book):
    """
    Safely resolve the PDF belonging to a book.

    Supports new records like:

        books/abc123_book.pdf

    and older records like:

        book.pdf
        /static/uploads/books/book.pdf
        static/uploads/books/book.pdf
        uploads/books/book.pdf
    """

    if not book or not book.pdf:

        return None


    upload_root = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).resolve()


    stored = str(
        book.pdf
    ).strip()


    # External PDF
    #
    # A Cloudinary URL cannot be safely converted
    # into a local Path.
    if stored.lower().startswith(
        ("http://", "https://")
    ):

        return None


    # Normalize slashes
    stored = stored.replace(
        "\\",
        "/",
    )


    # Remove old prefixes
    prefixes = [
        "/static/uploads/",
        "static/uploads/",
        "/uploads/",
        "uploads/",
    ]


    for prefix in prefixes:

        if stored.startswith(prefix):

            stored = stored[
                len(prefix):
            ]

            break


    # If only filename is stored,
    # assume books folder.
    if "/" not in stored:

        relative = Path(
            "books"
        ) / stored

    else:

        relative = Path(
            stored
        )


    # Security check
    if relative.is_absolute():

        return None


    if ".." in relative.parts:

        return None


    file_path = (
        upload_root / relative
    ).resolve()


    # Prevent path traversal
    try:

        file_path.relative_to(
            upload_root
        )

    except ValueError:

        return None


    if not file_path.is_file():

        return None


    if file_path.stat().st_size <= 0:

        return None


    return file_path


# =========================================================
# HOME
# =========================================================

@public_bp.route("/")
def home():

    latest_articles = (
        Article.query
        .filter(
            Article.is_published == True
        )
        .order_by(
            Article.created_at.desc()
        )
        .limit(3)
        .all()
    )


    latest_bayans = (
        Bayan.query
        .filter(
            Bayan.is_published == True
        )
        .order_by(
            Bayan.created_at.desc()
        )
        .limit(3)
        .all()
    )


    latest_gallery = (
        GalleryItem.query
        .filter(
            GalleryItem.is_published == True
        )
        .order_by(
            GalleryItem.created_at.desc()
        )
        .limit(6)
        .all()
    )


    latest_adab = (
        Adab.query
        .filter(
            Adab.is_published == True
        )
        .order_by(
            Adab.created_at.desc()
        )
        .limit(3)
        .all()
    )


    latest_online_book = (
        Book.query
        .filter(
            Book.is_published == True,
            Book.book_type.in_(
                ONLINE_BOOK_TYPES
            ),
        )
        .order_by(
            Book.created_at.desc()
        )
        .first()
    )


    latest_sell_book = (
        Book.query
        .filter(
            Book.is_published == True,
            Book.book_type.in_(
                SELL_BOOK_TYPES
            ),
        )
        .order_by(
            Book.created_at.desc()
        )
        .first()
    )


    return render_template(
        "index.html",
        latest_articles=latest_articles,
        latest_bayans=latest_bayans,
        latest_gallery=latest_gallery,
        latest_adab=latest_adab,
        latest_online_book=latest_online_book,
        latest_sell_book=latest_sell_book,
    )


# =========================================================
# ABOUT
# =========================================================

@public_bp.route("/about")
def about():

    return render_template(
        "about.html"
    )


# =========================================================
# ARTICLES
# =========================================================

@public_bp.route("/articles")
def articles():

    articles = (
        Article.query
        .filter(
            Article.is_published == True
        )
        .order_by(
            Article.created_at.desc()
        )
        .all()
    )


    return render_template(
        "articles.html",
        articles=articles,
    )


@public_bp.route(
    "/articles/<int:article_id>"
)
def article_detail(article_id):

    article = (
        Article.query
        .filter(
            Article.id == article_id,
            Article.is_published == True,
        )
        .first()
    )


    if not article:

        abort(404)


    return render_template(
        "article_detail.html",
        article=article,
    )


# =========================================================
# BAYANS
# =========================================================

@public_bp.route("/bayans")
def bayans():

    bayans = (
        Bayan.query
        .filter(
            Bayan.is_published == True
        )
        .order_by(
            Bayan.created_at.desc()
        )
        .all()
    )


    return render_template(
        "bayans.html",
        bayans=bayans,
    )


@public_bp.route(
    "/bayans/<int:bayan_id>"
)
def bayan_detail(bayan_id):

    bayan = (
        Bayan.query
        .filter(
            Bayan.id == bayan_id,
            Bayan.is_published == True,
        )
        .first()
    )


    if not bayan:

        abort(404)


    return render_template(
        "bayan_detail.html",
        bayan=bayan,
    )


@public_bp.route(
    "/bayans/<int:bayan_id>/watch"
)
def bayan_watch(bayan_id):

    bayan = (
        Bayan.query
        .filter(
            Bayan.id == bayan_id,
            Bayan.is_published == True,
        )
        .first()
    )


    if not bayan:

        abort(404)


    if bayan.upload_type == "upload":

        return render_template(
            "bayan_detail.html",
            bayan=bayan,
        )


    if bayan.video_url:

        return redirect(
            bayan.video_url
        )


    return render_template(
        "bayan_detail.html",
        bayan=bayan,
    )


# =========================================================
# BOOKS
# =========================================================

@public_bp.route("/books")
def books():

    books = (
        Book.query
        .filter(
            Book.is_published == True
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )


    return render_template(
        "books.html",
        books=books,
    )


@public_bp.route("/books/online")
def online_books():

    books = (
        Book.query
        .filter(
            Book.is_published == True,
            Book.book_type.in_(
                ONLINE_BOOK_TYPES
            ),
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )


    return render_template(
        "books.html",
        books=books,
    )


@public_bp.route("/books/buy")
def books_buy():

    books = (
        Book.query
        .filter(
            Book.is_published == True,
            Book.book_type.in_(
                SELL_BOOK_TYPES
            ),
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )


    return render_template(
        "books.html",
        books=books,
    )


# =========================================================
# BOOK READER PAGE
# =========================================================

@public_bp.route(
    "/books/<int:book_id>/read"
)
def book_reader(book_id):

    book = (
        Book.query
        .filter(
            Book.id == book_id,
            Book.is_published == True,
            Book.book_type.in_(
                ONLINE_BOOK_TYPES
            ),
        )
        .first()
    )


    if not book:

        abort(404)


    return render_template(
        "book_reader.html",
        book=book,
    )


# =========================================================
# BOOK PDF - OPEN IN BROWSER
# =========================================================

@public_bp.route(
    "/books/<int:book_id>/pdf"
)
def book_pdf(book_id):

    book = (
        Book.query
        .filter(
            Book.id == book_id,
            Book.is_published == True,
            Book.book_type.in_(
                ONLINE_BOOK_TYPES
            ),
        )
        .first()
    )


    if not book:

        abort(404)


    # Cloudinary/external URL
    if book.pdf and str(
        book.pdf
    ).lower().startswith(
        ("http://", "https://")
    ):

        return redirect(
            book.pdf
        )


    file_path = _book_pdf_path(
        book
    )


    if not file_path:

        abort(404)


    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=file_path.name,
        conditional=True,
    )


# =========================================================
# BOOK PDF - DOWNLOAD
# =========================================================

@public_bp.route(
    "/books/<int:book_id>/pdf/download"
)
def book_pdf_download(book_id):

    book = (
        Book.query
        .filter(
            Book.id == book_id,
            Book.is_published == True,
            Book.book_type.in_(
                ONLINE_BOOK_TYPES
            ),
        )
        .first()
    )


    if not book:

        abort(404)


    # External PDF
    if book.pdf and str(
        book.pdf
    ).lower().startswith(
        ("http://", "https://")
    ):

        return redirect(
            book.pdf
        )


    file_path = _book_pdf_path(
        book
    )


    if not file_path:

        abort(404)


    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=file_path.name,
        conditional=True,
    )


# =========================================================
# BOOK DETAIL
# =========================================================

@public_bp.route(
    "/books/<int:book_id>"
)
def book_detail(book_id):

    book = (
        Book.query
        .filter(
            Book.id == book_id,
            Book.is_published == True,
            Book.book_type.in_(
                SELL_BOOK_TYPES
            ),
        )
        .first()
    )


    if not book:

        abort(404)


    return render_template(
        "book_detail.html",
        book=book,
    )


# =========================================================
# BOOK ORDER
# =========================================================

@public_bp.route(
    "/books/<int:book_id>/order",
    methods=["GET", "POST"],
)
def book_order(book_id):

    book = (
        Book.query
        .filter(
            Book.id == book_id,
            Book.is_published == True,
            Book.book_type.in_(
                SELL_BOOK_TYPES
            ),
        )
        .first()
    )


    if not book:

        abort(404)


    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()


        phone = request.form.get(
            "phone",
            "",
        ).strip()


        address = request.form.get(
            "address",
            "",
        ).strip()


        if (
            not name
            or not phone
            or not address
        ):

            flash(
                "Please fill all required fields.",
                "error",
            )

            return render_template(
                "book_order.html",
                book=book,
            )


        flash(
            "Your order request has been received.",
            "success",
        )


        return redirect(
            url_for(
                "public.book_detail",
                book_id=book.id,
            )
        )


    return render_template(
        "book_order.html",
        book=book,
    )


# =========================================================
# ADAB
# =========================================================

@public_bp.route("/adab")
def adab():

    items = (
        Adab.query
        .filter(
            Adab.is_published == True
        )
        .order_by(
            Adab.created_at.desc()
        )
        .all()
    )


    return render_template(
        "adab.html",
        items=items,
    )


@public_bp.route(
    "/adab/<int:item_id>"
)
def adab_detail(item_id):

    item = (
        Adab.query
        .filter(
            Adab.id == item_id,
            Adab.is_published == True,
        )
        .first()
    )


    if not item:

        abort(404)


    return render_template(
        "adab_detail.html",
        item=item,
    )


# =========================================================
# GALLERY
# =========================================================

@public_bp.route("/gallery")
def gallery():

    items = (
        GalleryItem.query
        .filter(
            GalleryItem.is_published == True
        )
        .order_by(
            GalleryItem.created_at.desc()
        )
        .all()
    )


    return render_template(
        "gallery.html",
        items=items,
    )


# =========================================================
# CONTACT
# =========================================================

@public_bp.route(
    "/contact",
    methods=["GET", "POST"],
)
def contact():

    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()


        email = request.form.get(
            "email",
            "",
        ).strip()


        message = request.form.get(
            "message",
            "",
        ).strip()


        if (
            not name
            or not email
            or not message
        ):

            flash(
                "Please fill all required fields.",
                "error",
            )

            return render_template(
                "contact.html"
            )


        item = ContactMessage(
            name=name,
            email=email,
            message=message,
            status="New",
        )


        db.session.add(item)

        db.session.commit()


        flash(
            "Your message has been sent successfully.",
            "success",
        )


        return redirect(
            url_for(
                "public.contact"
            )
        )


    return render_template(
        "contact.html"
    )