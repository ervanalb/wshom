import flask_login
import werkzeug.security
from wshom.extensions import db

friendship = db.Table(
    "friendships", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False),
    db.Column("friend_id", db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
)

class User(flask_login.UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    display_name = db.Column(db.String(240), nullable=False, default="")
    timezone = db.Column(db.String(120), nullable=False, default="")
    min_interval = db.Column(db.Integer, nullable=False, default=5)

    friends = db.relationship("User", secondary=friendship, 
                                      primaryjoin=id==friendship.c.user_id,
                                      secondaryjoin=id==friendship.c.friend_id,
    )

    def __repr__(self):
        return "<User {}>".format(self.username)

    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.password_hash, password)

class GraphNode(db.Model):
    __tablename__ = "graph_nodes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

class GraphEdge(db.Model):
    __tablename__ = "graph_edges"

    user_a_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
