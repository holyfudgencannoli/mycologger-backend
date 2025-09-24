from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..models import User, Task
from ..db import SessionLocal

auth_bp = Blueprint('authentication', __name__)

def get_user_by_username(username):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(username=username).first()
    db_session.close()
    if user:
        # return consistent keys
        return {
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash,
            "is_admin": user.is_admin
        }
    return None



def check_password(user, password):
    if not user or "password_hash" not in user:
        return False
    return check_password_hash(user["password_hash"], password)


@auth_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    user = get_user_by_username(data['username'])
    if user and check_password(user, data['password']):
        if user['is_admin']:
            additional_claims = {"is_admin": True}
            access_token = create_access_token(identity=str(user['id']), additional_claims=additional_claims)
        access_token = create_access_token(identity=str(user['id']))

        user_data = {"id": user["id"], "username": user["username"]}
        return jsonify({'access_token': access_token, 'user': user_data}), 200
    return jsonify({"msg": "Bad username or password"}), 401

BLACKLIST = set()

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return jsonify(msg="Successfully logged out"), 200
