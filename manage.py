from flask.ext.script import Manager

from stackquery.dashboard import app

if __name__ == "__main__":
    manager = Manager(app.create_app())
    manager.run()
