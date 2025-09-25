from flask import jsonify, Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..db import SessionLocal
from ..models import RawMaterial
from datetime import datetime

raw_materials_bp = Blueprint('raw_materials', __name__)

@raw_materials_bp.route("/", methods=["GET"])
@jwt_required()
def list_raw_materials():
    db_session = SessionLocal()

    raw_materials = db_session.query(RawMaterial).all()

    raw_materials_serialized = [u.to_dict() for u in raw_materials]

    db_session.close()

    return jsonify({'raw_materials': raw_materials_serialized}), 200


@raw_materials_bp.route("/", methods=["POST"])
@jwt_required()
def register_raw_material():
    db_session = SessionLocal()
    data = request.form

    name = data.get('name')
    created_at = datetime.now()

    already_there =  db_session.query(RawMaterial).filter_by(name=name).first()

    if not already_there:
        new_item = RawMaterial(
            name = name,
            created_at = created_at
        )
        db_session.add(new_item)
        db_session.commit()
        db_session.close()
        return jsonify({"msg": "RawMaterial created"}), 201
    else:
        return jsonify({"msg": "RawMaterial already exists"}), 400


@raw_materials_bp.route("/<int:raw_material_id>", methods=["GET"])
@jwt_required()
def get_raw_material(raw_material_id):
    db_session = SessionLocal()

    raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

    if raw_material:
        return jsonify({'raw_material': raw_material})
    else:
        return "", 404

@raw_materials_bp.route("/<int:raw_material_id>", methods=["PUT"])
@jwt_required()
def update_raw_material(raw_material_id):
    db_session = SessionLocal()
    
    data = request.form

    name = data.get('name')

    raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

    raw_material.name = name       #type: ignore

    db_session.close()

    return jsonify({'success': True}), 200

@raw_materials_bp.route("/<int:raw_material_id>", methods=["DELETE"])
@jwt_required()
def delete_raw_material(raw_material_id):
    db_session = SessionLocal()

    raw_material = db_session.query(RawMaterial).filter_by(id=raw_material_id).first()

    db_session.delete(raw_material)
    db_session.commit()
    db_session.close()

    return "", 204


