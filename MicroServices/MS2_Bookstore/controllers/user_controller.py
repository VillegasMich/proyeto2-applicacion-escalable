from http import HTTPStatus
from flask import Blueprint, request, session

from extensions import db
from models.user import User


user = Blueprint("user", __name__)


@user.route("/create", methods=["POST"])
def create():
    id = request.get_json().get("id")
    name = request.get_json().get("name")
    email = request.get_json().get("email")
    new_user = User()
    new_user.id = id
    new_user.name = name
    new_user.email = email
    db.session.add(new_user)
    db.session.commit()
    return {"status": HTTPStatus.CREATED}


@user.route("/set-current", methods=["POST"])
def set_current():
    user_id = request.get_json().get("id")
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    # Store minimal user info in session
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["authenticated"] = True
    return {"status": HTTPStatus.OK}
