from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from ..models import User
from ..db import SessionLocal

users_bp = Blueprint('users', __name__)

def create_user(username, password_hash, email, phone, is_admin):
    db_session = SessionLocal()
    already_there = db_session.query(User).filter(User.username==username).first()

    if not already_there:
        user = User(
            username=username,
            email=email,
            is_admin=is_admin,
            phone=phone,
            password_hash=password_hash,
            provider="local"
        )

        db_session.add(user)
        db_session.commit()
    else:
        raise ValueError("User already exists")
    db_session.close()


@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    db_session = SessionLocal()

    users = db_session.query(User).all()

    users_serialized = [u.to_dict() for u in users]

    db_session.close()

    return jsonify({'users': users_serialized}), 200


@users_bp.route("/", methods=["POST"])
@jwt_required()
def register_user():
    data = request.form

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    isAdmin = data.get('is_admin')

    if isAdmin == 'admin123':
        is_admin = True
    else:
        is_admin = False

    password_hash = generate_password_hash(data.get('password'))        #type: ignore

    try:
        create_user(username, password_hash, email, phone, is_admin)
    except ValueError:
        return jsonify({"msg": "User already exists"}), 400
    return jsonify({"msg": "User created"}), 201

@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    db_session = SessionLocal()

    user = db_session.query(User).filter_by(id=user_id).first()

    if user:
        return jsonify({'user': user})
    else:
        return "", 404

@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    db_session = SessionLocal()
    
    data = request.form

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    isAdmin = data.get('is_admin')

    user = db_session.query(User).filter_by(id=user_id).first()

    user.username = username       #type: ignore
    user.email = email       #type: ignore
    user.phone = phone       #type: ignore
    user.is_admin = isAdmin       #type: ignore

    db_session.close()

    return jsonify({'success': True}), 200

@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    db_session = SessionLocal()

    user = db_session.query(User).filter_by(id=user_id).first()

    db_session.delete(user)
    db_session.commit()
    db_session.close()

    return "", 204