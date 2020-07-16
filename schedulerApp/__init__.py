import psycopg2

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_NAME='schedulerdb',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import member
    app.register_blueprint(member.bp)
    app.add_url_rule('/', endpoint='index')

    from . import organization
    app.register_blueprint(organization.bp)    

    from . import util
    from . import validate
    from . import update_db
    from . import query_db

    return app    