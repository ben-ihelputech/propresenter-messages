import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'kids_messages.sqlite'),
        PP_HOST='localhost',
        PP_PORT=1025,
        PP_API_VERSION='v1',
        ALLOW_REGISTRATION=True,
        DISPLAY_TIME=30         # Time in seconds that the message will be displayed
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple health page
    @app.route('/health')
    def hello():
        return 'HEALTH OK'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import messages
    app.register_blueprint(messages.bp)
    app.add_url_rule('/', endpoint='index')

    return app