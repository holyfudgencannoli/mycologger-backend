from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..models import RawMaterialPurchaseLog, RawMaterial, RawMaterialInventoryLog, Vendor
from ..db import SessionLocal

purchase_logs_bp = Blueprint('purchase_logs', __name__)

@purchase_logs_bp.route("/raw-materials", methods=["GET"])
@jwt_required()
def list_raw_material_purchase_logs():
    db_session = SessionLocal()

    raw_material_purchase_logs = db_session.query(RawMaterialPurchaseLog).all()

    raw_material_purchase_logs_serialized = [r.to_dict() for r in raw_material_purchase_logs]

    db_session.close()

    return jsonify({'raw_material_purchase_logs': raw_material_purchase_logs_serialized}), 200


@purchase_logs_bp.route("/raw-materials", methods=["POST"])
@jwt_required()
def register_raw_material_purchase_log():
    db_session = SessionLocal()

    user_id = get_jwt_identity()

    data = request.get_json()

    log_date = data['log_date']
    purchase_date = data['purchase_date']
    purchase_amount = data['purchase_amount']
    purchase_unit = data['purchase_unit']
    cost = data['cost']
    notes = data['notes']
    item_id = data['item_id']
    vendor_id = data['vendor_id']
    raw_material_inventory_log_id = data['raw_material_inventory_log_id']

    try:
        new_log = RawMaterialPurchaseLog(
            log_date = log_date,
            purchase_date = purchase_date,
            purchase_amount = purchase_amount,
            purchase_unit = purchase_unit,
            cost = cost,
            notes = notes,
            item_id = item_id,
            vendor_id = vendor_id,
            raw_material_inventory_log_id = raw_material_inventory_log_id
        )
        db_session.add(new_log)
        db_session.flush()

        if not item_id:
            new_item = RawMaterial(

            )

            db_session.add(new_item)

        else:
            pass

        if not vendor_id:
            name = data['name']
            phone = data['phone']
            email = data['email']
            website = data['website']

            new_vendor = Vendor(
                name = name,
                phone = phone,
                email = email,
                website = website
            )

            db_session.add(new_vendor)

        else: 
            pass

        if not raw_material_inventory_log_id:
            new_inventory_log = RawMaterialInventoryLog(

            )

            db_session.add(new_inventory_log)

        else: 
            pass

    except KeyError:
        return jsonify({"msg": "Data not working"}), 400
    
    finally: 
        db_session.commit()

    return jsonify({"msg": "User created"}), 201

@purchase_logs_bp.route("/raw-materials/<int:raw_material_purchase_log_id>", methods=["GET"])
@jwt_required()
def get_raw_material_purchase_log(raw_material_purchase_log_id):
    db_session = SessionLocal()

    raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_purchase_log_id).first()

    if raw_material_purchase_log:
        return jsonify({'raw_material_purchase_log': raw_material_purchase_log})
    else:
        return "", 404

@purchase_logs_bp.route("/raw-materials/<int:raw_material_purchase_log_id>", methods=["PUT"])
@jwt_required()
def update_raw_material_purchase_log(raw_material_purchase_log_id):
    db_session = SessionLocal()

    data = request.get_json()

    purchase_date = data['purchase_date']
    purchase_amount = data['purchase_amount']
    purchase_unit = data['purchase_unit']
    cost = data['cost']
    notes = data['notes']
    item_id = data['item_id']
    vendor_id = data['vendor_id']
    raw_material_inventory_log_id = data['raw_material_inventory_log_id']
        
    raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_purchase_log_id).first()

    raw_material_purchase_log.purchase_date = purchase_date       #type: ignore
    raw_material_purchase_log.purchase_amount = purchase_amount       #type: ignore
    raw_material_purchase_log.purchase_unit = purchase_unit       #type: ignore
    raw_material_purchase_log.cost = cost       #type: ignore
    raw_material_purchase_log.notes = notes       #type: ignore
    raw_material_purchase_log.item_id = item_id       #type: ignore
    raw_material_purchase_log.vendor_id = vendor_id       #type: ignore
    raw_material_purchase_log.raw_material_inventory_log_id = raw_material_inventory_log_id       #type: ignore

    db_session.close()

    return jsonify({'success': True}), 200

@purchase_logs_bp.route("/raw-materials/<int:raw_material_inventory_log_id>", methods=["DELETE"])
@jwt_required()
def delete_raw_material_purchase_log(raw_material_inventory_log_id):
    db_session = SessionLocal()

    raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_inventory_log_id).first()

    db_session.delete(raw_material_purchase_log)
    db_session.commit()
    db_session.close()

    return "", 204