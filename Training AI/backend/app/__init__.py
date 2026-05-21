from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os

# these objects are imported by other modules to avoid circular imports
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(async_mode='eventlet')


def create_app(config_object=None):
    """Application factory.

    If you want to customise settings you can pass a config object or
    rely on environment variables.
    """
    app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'frontend'), static_url_path='/')

    # basic configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/picupai')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
    if config_object:
        app.config.from_object(config_object)

    # initialise extensions
    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)
    socketio.init_app(app)

    # register blueprints
    from .auth import auth_bp
    from .routes.qa import qa_bp
    from .routes.team_leader import team_leader_bp
    from .routes.admin import admin_bp
    from .routes.livechat import livechat_bp
    from .routes.backoffice_auth import backoffice_auth_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(qa_bp, url_prefix='/qa')
    app.register_blueprint(team_leader_bp, url_prefix='/team')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(livechat_bp, url_prefix='/livechat')
    app.register_blueprint(backoffice_auth_bp, url_prefix='/backoffice')

    # static frontend catch-all (SPA support)
    from flask import send_from_directory

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        frontend_dir = os.path.join(os.getcwd(), 'frontend')
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory('frontend', path)
        else:
            return send_from_directory('frontend', 'index.html')

    return app


# global application instance for simple scripts / WSGI
# Only create app if not imported for testing
if __name__ != '__main__':
    app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
