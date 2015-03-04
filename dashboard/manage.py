from flask.ext.script import Manager
import app


if __name__ == "__main__":

    manager = Manager(app.app)
    manager.run()
