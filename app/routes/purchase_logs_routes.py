from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime
from ..models import RawMaterialPurchaseLog, RawMaterial, RawMaterialInventoryLog, Vendor, ReceiptEntry
from ..db import SessionLocal

purchase_logs_bp = Blueprint('purchase_logs', __name__)

@purchase_logs_bp.route("/raw-materials", methods=["GET"])
@jwt_required()
def list_raw_material_purchase_logs():
    with SessionLocal() as db_session:

        raw_material_purchase_logs = db_session.query(RawMaterialPurchaseLog).all()

        raw_material_purchase_logs_serialized = [r.to_dict() for r in raw_material_purchase_logs]


        return jsonify({'raw_material_purchase_logs': raw_material_purchase_logs_serialized}), 200
@purchase_logs_bp.route("/raw-materials", methods=["POST"])
@jwt_required()
def register_raw_material_purchase_log():
    with SessionLocal() as db_session:
        user_id = get_jwt_identity()
        data = request.get_json()

        name = data['name']
        brand = data['brand']
        purchase_date = datetime.strptime(data['purchaseDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
        purchase_quantity = data['purchaseQuantity']
        purchase_unit = data['purchaseUnit']
        inventory_quantity = data['inventoryQuantity']
        inventory_unit = data['inventoryUnit']
        cost = data['cost']
        notes = data['notes']

        # ------------------- Vendor Handling -------------------
        vendor_name = data['vendor']
        vendor = db_session.query(Vendor).filter_by(name=vendor_name).first()
        if not vendor:
            vendor = Vendor(
                name=vendor_name,
                phone=data['vendorPhone'],
                email=data['vendorEmail'],
                website=data['vendorWebsite']
            )
            db_session.add(vendor)
            db_session.flush()  # ensures vendor.id is set

        # ------------------- Raw Material Handling -------------------
        raw_material = db_session.query(RawMaterial).filter_by(name=name).first()
        if not raw_material:
            raw_material = RawMaterial(
                name=name,
                category=data['category'],
                subcategory=data['subcategory'],
                created_at=datetime.now()
            )
            inventory_log = RawMaterialInventoryLog(
                amount_on_hand=inventory_quantity,
                amount_on_hand_unit=inventory_unit,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            raw_material.inventory_log = inventory_log
            db_session.add(raw_material)
            db_session.flush()
        else:
            inventory_log = raw_material.get_inventory_log()  # type: ignore
            if inventory_log:
                inventory_log.amount_on_hand = (inventory_log.amount_on_hand or 0) + inventory_quantity
                inventory_log.last_updated = datetime.now()

        # ------------------- Purchase Log -------------------
        purchase_log = RawMaterialPurchaseLog(
            brand=brand,
            log_date=datetime.now(),
            purchase_date=purchase_date,
            purchase_amount=purchase_quantity,
            purchase_unit=purchase_unit,
            cost=cost,
            notes=notes,
            item=raw_material,
            vendor=vendor,
            inventory_log=inventory_log,
            user_id=user_id
        )
        db_session.add(purchase_log)
        db_session.flush()

        # ------------------- Receipt Entry -------------------
        receipt = ReceiptEntry(
            date=purchase_date,
            filename=data['filename'],
            image_url=data['imageUrl'],
            created_at=datetime.now(),
            memo=data['receiptMemo'],
            purchase_log=purchase_log,
            vendor=vendor,
            user_id=user_id
        )
        db_session.add(receipt)
        db_session.commit()

        return jsonify({"msg": "Purchase Log created"}), 201


@purchase_logs_bp.route("/raw-materials/<int:raw_material_purchase_log_id>", methods=["GET"])
@jwt_required()
def get_raw_material_purchase_log(raw_material_purchase_log_id):
    with SessionLocal() as db_session:

        raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_purchase_log_id).first()

        if not raw_material_purchase_log:
            return jsonify({"msg": "Not found"}), 404
        return jsonify({'raw_material_purchase_log': raw_material_purchase_log.to_dict()})

@purchase_logs_bp.route("/raw-materials/<int:raw_material_purchase_log_id>", methods=["PUT"])
@jwt_required()
def update_raw_material_purchase_log(raw_material_purchase_log_id):
    with SessionLocal() as db_session:
        raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_purchase_log_id).first()

        if not raw_material_purchase_log:
            return jsonify({"msg": "Not found"}), 404

        data = request.get_json()

        purchase_date = data['purchase_date']
        purchase_amount = data['purchase_amount']
        purchase_unit = data['purchase_unit']
        cost = data['cost']
        notes = data['notes']
        item_id = data['item_id']
        vendor_id = data['vendor_id']
        raw_material_inventory_log_id = data['raw_material_inventory_log_id']
            

        raw_material_purchase_log.purchase_date = purchase_date       #type: ignore
        raw_material_purchase_log.purchase_amount = purchase_amount       #type: ignore
        raw_material_purchase_log.purchase_unit = purchase_unit       #type: ignore
        raw_material_purchase_log.cost = cost       #type: ignore
        raw_material_purchase_log.notes = notes       #type: ignore
        raw_material_purchase_log.item_id = item_id       #type: ignore
        raw_material_purchase_log.vendor_id = vendor_id       #type: ignore
        raw_material_purchase_log.raw_material_inventory_log_id = raw_material_inventory_log_id       #type: ignore

        db_session.commit()


        return jsonify({'success': True}), 200

@purchase_logs_bp.route("/raw-materials/<int:raw_material_purchase_log_id>", methods=["DELETE"])
@jwt_required()
def delete_raw_material_purchase_log(raw_material_purchase_log_id):
    with SessionLocal() as db_session:

        raw_material_purchase_log = db_session.query(RawMaterialPurchaseLog).filter_by(id=raw_material_purchase_log_id).first()

        if not raw_material_purchase_log:
            return jsonify({"msg": "Not found"}), 404

        db_session.delete(raw_material_purchase_log)
        db_session.commit()

        return "", 204