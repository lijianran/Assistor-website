import os

from flask import Flask

# from datetime import timedelta


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'hello,world!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # from . import blog
    # app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')\

    from .lijing import lijing_index
    app.register_blueprint(lijing_index.bp)
    app.add_url_rule('/', endpoint='lijing.index')

    # from . import lijing
    from .lijing import lijing_basicinfo
    app.register_blueprint(lijing_basicinfo.bp)

    from .lijing import lijing_workinfo
    app.register_blueprint(lijing_workinfo.bp)

    from .lijing import lijing_honorinfo
    app.register_blueprint(lijing_honorinfo.bp)

    from .lijing import lijing_search
    app.register_blueprint(lijing_search.bp)

    from .lijing import bonus_calculator
    app.register_blueprint(bonus_calculator.bp)

    return app
