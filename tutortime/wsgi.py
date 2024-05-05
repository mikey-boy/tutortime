import eventlet

eventlet.patcher.monkey_patch()

from tutortime.app import create_app

application = create_app()
