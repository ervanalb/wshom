import flask_login
import werkzeug.security
from wshom.extensions import db

friendship = db.Table(
    "friendships", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("friend_id", db.Integer, db.ForeignKey("users.id"), primary_key=True)
)

class User(flask_login.UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    friends = db.relationship("User", secondary=friendship, 
                                      primaryjoin=id==friendship.c.user_id,
                                      secondaryjoin=id==friendship.c.friend_id,
    )

    def __repr__(self):
        return "<User {}>".format(self.username)

    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.password_hash, password)

