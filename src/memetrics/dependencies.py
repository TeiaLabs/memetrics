from tauth.dependencies import security


def init_dependencies(app):
    security.init_app(app)
