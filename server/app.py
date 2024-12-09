#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        request_json = request.get_json()
        
        user = User(
            username = request_json.get("username"),
            image_url = request_json.get("image_url"),
            bio = request_json.get("bio")
        )
        user.password_hash = request_json.get("password")

        try:
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user.to_dict(), 201

        except IntegrityError:
            return {"error": "Unprocessable entity"}, 422

class CheckSession(Resource):
    def get(self):
        if (user_id := session["user_id"]) and (user := User.query.filter_by(id=user_id).first()):
            return user.to_dict(), 200
        else:
            return {}, 401
    pass

class Login(Resource):
    def post(self):
        request_json = request.get_json();

        
        if (user := User.query.filter_by(username=request_json.get("username")).first()) \
            and user.authenticate(request_json.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200
        else:
            return {}, 401
    pass

class Logout(Resource):
    def delete(self):
        if not session["user_id"]:
            return {"error":"Unauthorized"}, 401
        
        session["user_id"] = None
        return {}, 204
    pass

class RecipeIndex(Resource):
    def get(self):
        if not session["user_id"]:
            return {"error":"Unauthorized"}, 401
        
        return [recipe.to_dict() for recipe in Recipe.query.filter_by(user_id=session["user_id"]).all()], 200

    def post(self):
        if not session["user_id"]:
            return {"error":"Unauthorized"}, 401


        try:
            request_json = request.get_json()

            recipe = Recipe(
                title=request_json.get("title"),
                instructions=request_json.get("instructions"),
                minutes_to_complete=request_json.get("minutes_to_complete"),
                user_id=session["user_id"],
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201
        except (IntegrityError, ValueError):
            return {"error": "Unprocessable entity"}, 422
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)