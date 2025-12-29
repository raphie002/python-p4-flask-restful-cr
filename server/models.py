# server/models.py
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy_serializer import SerializerMixin # type: ignore

# Add this naming convention dictionary
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Pass the metadata to SQLAlchemy
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Prevent recursion: don't show the user inside their own newsletter list
    serialize_rules = ('-newsletters.user',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    newsletters = db.relationship('Newsletter', back_populates='user')

class Newsletter(db.Model, SerializerMixin):
    __tablename__ = 'newsletters'

    # Prevent recursion: don't show the newsletter list inside the author object
    serialize_rules = ('-user.newsletters',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    published_at = db.Column(db.DateTime, server_default=db.func.now())
    edited_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationship
    user = db.relationship('User', back_populates='newsletters')

    def __repr__(self):
        return f'<Newsletter {self.title} by User {self.user_id}>'