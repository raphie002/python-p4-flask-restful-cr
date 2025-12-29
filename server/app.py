#!/usr/bin/env python3
# server/app.py
from flask import Flask, request, make_response
from flask_migrate import Migrate # type: ignore
from flask_restful import Api, Resource, reqparse # type: ignore
from models import db, Newsletter, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# --- CUSTOM VALIDATION ---
def validate_title(value):
    if len(value) < 5:
        raise ValueError("Title must be at least 5 characters long")
    return value

# --- REQUEST PARSERS ---
newsletter_parser = reqparse.RequestParser()
newsletter_parser.add_argument('title', type=validate_title, required=True, help="Title is required")
newsletter_parser.add_argument('body', type=str, required=True, help="Body is required")
newsletter_parser.add_argument('user_id', type=int, required=True, help="User ID is required")

# Create a copy for PATCH (where fields are optional)
patch_parser = newsletter_parser.copy()
for arg in patch_parser.args:
    arg.required = False

# --- RESOURCES ---
class Home(Resource):
    def get(self):
        return {"message": "Welcome to the Newsletter RESTful API"}, 200

class Newsletters(Resource):
    def get(self):
        newsletters = [n.to_dict() for n in Newsletter.query.all()]
        return make_response(newsletters, 200)

    def post(self):
        args = newsletter_parser.parse_args()
        new_newsletter = Newsletter(**args)
        db.session.add(new_newsletter)
        db.session.commit()
        return make_response(new_newsletter.to_dict(), 201)

class NewsletterByID(Resource):
    def get(self, id):
        n = Newsletter.query.filter_by(id=id).first()
        if not n: return {"error": "Not found"}, 404
        return make_response(n.to_dict(), 200)

    def patch(self, id):
        n = Newsletter.query.filter_by(id=id).first()
        if not n: return {"error": "Not found"}, 404
        
        args = patch_parser.parse_args()
        for key, value in args.items():
            if value is not None:
                setattr(n, key, value)
        
        db.session.commit()
        return make_response(n.to_dict(), 200)

    def delete(self, id):
        n = Newsletter.query.filter_by(id=id).first()
        if not n: return {"error": "Not found"}, 404
        db.session.delete(n)
        db.session.commit()
        return '', 204

class UserByID(Resource):
    def get(self, id):
        u = User.query.filter_by(id=id).first()
        if not u: return {"error": "User not found"}, 404
        return make_response(u.to_dict(), 200)

# --- ROUTES ---
api.add_resource(Home, '/')
api.add_resource(Newsletters, '/newsletters')
api.add_resource(NewsletterByID, '/newsletters/<int:id>')
api.add_resource(UserByID, '/users/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)