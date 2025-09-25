from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..db import SessionLocal
from ..models import Task


tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/", methods=["GET"])
@jwt_required()
def list_tasks():
    db_session = SessionLocal()

    tasks = db_session.query(Task).all()

    tasks_serialized = [t.to_dict() for t in tasks]

    db_session.close()

    return jsonify({'tasks': tasks_serialized}), 200


@tasks_bp.route("/", methods=["POST"])
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


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    db_session = SessionLocal()

    task = db_session.query(Task).filter_by(id=task_id).first()

    if task:
        return jsonify({'task': task})
    else:
        return "", 404

@tasks_bp.route("/<int:task_id>", methods=["PUT"])
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

@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    db_session = SessionLocal()

    task = db_session.query(Task).filter_by(id=task_id).first()

    db_session.delete(task)
    db_session.commit()
    db_session.close()

    return "", 204