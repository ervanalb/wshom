import flask
import flask_sqlalchemy
import wshom.config

app = flask.Flask(__name__)
app.config.from_object(wshom.config.Config)
db = flask_sqlalchemy.SQLAlchemy(app)

import wshom.login

@app.route("/")
def index():
    return flask.render_template("index.html")

db.create_all()
