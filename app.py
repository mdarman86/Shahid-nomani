from flask import Flask, render_template
from dotenv import load_dotenv

from config import Config
from extensions import db, login_manager, csrf, migrate
from models import Admin
from services.media import media_url

load_dotenv()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)


    # =====================================================
    # EXTENSIONS
    # =====================================================

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)


    # =====================================================
    # TEMPLATE HELPERS
    # =====================================================

    @app.context_processor
    def inject_helpers():

        return {
            "media_url": media_url,

            "social_links": {

                "facebook":
                    "https://www.facebook.com/shahid.nomani.al.misbahi",

                "instagram":
                    "https://www.instagram.com/shahidnomani07/",

                "youtube":
                    "",

                "twitter":
                    "",

                "telegram":
                    "",

                "whatsapp":
                    "",
            },
        }


    # =====================================================
    # BLUEPRINTS
    # =====================================================

    from routes.public import public_bp
    from routes.admin import admin_bp

    app.register_blueprint(
        public_bp
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin",
    )


    # =====================================================
    # LOGIN MANAGER
    # =====================================================

    @login_manager.user_loader
    def load_user(user_id):

        try:

            return db.session.get(
                Admin,
                int(user_id),
            )

        except (
            TypeError,
            ValueError,
        ):

            return None


    # =====================================================
    # ERROR HANDLERS
    # =====================================================

    @app.errorhandler(404)
    def not_found(error):

        return render_template(
            "404.html"
        ), 404


    @app.errorhandler(500)
    def server_error(error):

        db.session.rollback()

        return render_template(
            "500.html"
        ), 500


    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )