import eventlet

eventlet.patcher.monkey_patch()

from tutortime.app import create_app


def main(config=None):
    app = create_app(config=config)
    return app
