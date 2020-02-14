import flask
import wshom.config

app = flask.Flask(__name__)
app.config.from_object(wshom.config.Config)

import wshom.login

@app.route("/")
def index():
    return flask.render_template("index.html")
