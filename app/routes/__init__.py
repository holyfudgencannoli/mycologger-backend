from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..models import User, Task
from ..db import SessionLocal

app_bp = Blueprint('app', __name__)

# Helper functions
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

    
def get_user_by_user_id(user_id):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(id=user_id).first()
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

@app_bp.route("/auth/login", methods=['POST'])
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

@app_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return jsonify(msg="Successfully logged out"), 200

@app_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    db_session = SessionLocal()

    users = db_session.query(User).all()

    users_serialized = [u.to_dict() for u in users]

    db_session.close()

    return jsonify({'users': users_serialized}), 200


@app_bp.route("/users", methods=["POST"])
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

@app_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    db_session = SessionLocal()

    user = db_session.query(User).filter_by(id=user_id).first()

    if user:
        return jsonify({'user': user})
    else:
        return "", 404

@app_bp.route("/users/<int:user_id>", methods=["PUT"])
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

@app_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    db_session = SessionLocal()

    user = db_session.query(User).filter_by(id=user_id).first()

    db_session.delete(user)
    db_session.commit()
    db_session.close()

    return "", 204

# @app_bp.route("/raw-materials", methods=["GET"])
# @jwt_required()
# def list_raw_materials():
#     db_session = SessionLocal()

#     raw_materials = db_session.query(RawMaterial).all()

#     raw_materials_serialized = [u.to_dict() for u in raw_materials]

#     db_session.close()

#     return jsonify({'raw_materials': raw_materials_serialized}), 200


# @app_bp.route("/raw-materials", methods=["POST"])
# @jwt_required()
# def register_raw_material():
#     db_session = SessionLocal()
#     data = request.form

#     name = data.get('name')
#     created_at = datetime.now()

#     already_there =  db_session.query(RawMaterial).filter_by(name=name).first()

#     if not already_there:
#         new_item = RawMaterial(
#             name = name,
#             created_at = created_at
#         )
#         db_session.add(new_item)
#         db_session.commit()
#         db_session.close()
#         return jsonify({"msg": "RawMaterial created"}), 201
#     else:
#         return jsonify({"msg": "RawMaterial already exists"}), 400


# @app_bp.route("/raw-materials/<int:raw_material_id>", methods=["GET"])
# @jwt_required()
# def get_raw_material(raw_material_id):
#     db_session = SessionLocal()

#     raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

#     if raw_material:
#         return jsonify({'raw_material': raw_material})
#     else:
#         return "", 404

# @app_bp.route("/raw-materials/<int:raw_material_id>", methods=["PUT"])
# @jwt_required()
# def update_raw_material(raw_material_id):
#     db_session = SessionLocal()
    
#     data = request.form

#     name = data.get('name')

#     raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

#     raw_material.name = name       #type: ignore

#     db_session.close()

#     return jsonify({'success': True}), 200

# @app_bp.route("/raw-materials/<int:raw_material_id>", methods=["DELETE"])
# @jwt_required()
# def delete_raw_material(raw_material_id):
#     db_session = SessionLocal()

#     raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

#     db_session.delete(raw_material)
#     db_session.commit()
#     db_session.close()

#     return "", 204


@app_bp.route("/tasks-get", methods=["GET"])
# @jwt_required()
def list_tasks():
    db_session = SessionLocal()

    tasks = db_session.query(Task).all()

    tasks_serialized = [t.to_dict() for t in tasks]

    db_session.close()

    return jsonify({'tasks': tasks_serialized}), 200


@app_bp.route("/tasks", methods=["POST"])
@jwt_required()
def register_task():
    db_session = SessionLocal()

    user_id = get_jwt_identity()

    data = request.get_json()

    name = data['name']
    description = data['description']
    start_datetime = data['start']
    end_datetime = data['end']
    memo = data['memo']

    parsed_start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S.%fZ") #type: ignore
    parsed_end_datetime =  datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S.%fZ") #type: ignore
    total_time = (parsed_end_datetime - parsed_start_datetime).total_seconds()


    new_task = Task(
        name = name,
        description = description,
        start_datetime = parsed_start_datetime,
        end_datetime =  parsed_end_datetime,
        total_time = total_time, #type: ignore
        memo = memo,
        user_id = user_id
    )
    db_session.add(new_task)
    db_session.commit()
    db_session.close()
    return jsonify({"msg": "Task created"}), 201


@app_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    db_session = SessionLocal()

    task = db_session.query(Task).filter_by(id=task_id).first()

    if task:
        return jsonify({'task': task})
    else:
        return "", 404

@app_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    db_session = SessionLocal()
    
    data = request.get_json()

    name = data['name']
    description = data['description']
    memo = data['memo']

    task = db_session.query(Task).filter_by(id=task_id).first()

    task.name = name       #type: ignore
    task.description = description       #type: ignore
    task.memo = memo       #type: ignore

    db_session.close()

    return jsonify({'success': True}), 200

@app_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    db_session = SessionLocal()

    task = db_session.query(Task).filter_by(id=task_id).first()

    db_session.delete(task)
    db_session.commit()
    db_session.close()

    return "", 204