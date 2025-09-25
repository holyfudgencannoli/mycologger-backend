from flask import Blueprint, jsonify, request, session
from datetime import datetime
from ..db import db_session
from ..models import ReceiptDataObject, Receipt, User, ACCOUNT_ID, BUCKET_NAME, ACCESS_KEY_ID, SECRET_ACCESS_KEY
import os
import boto3
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required

receipts_bp = Blueprint('receipts', __name__)

s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name="auto",
)

# -------------------------
# 1. Signed URL generator
# -------------------------
@receipts_bp.route('/get-upload-url', methods=['POST'])
@login_required
def get_upload_url():
    """Generate a presigned URL so frontend can upload directly to R2"""
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    # Secure + unique filename (user_id + timestamp + ext)
    ext = os.path.splitext(filename)[1].lower()
    safe_name = secure_filename(filename)
    object_key = f"user_{current_user.id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe_name}"

    # Presigned URL for direct upload
    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET_NAME, "Key": object_key},
        ExpiresIn=300  # 5 minutes
    )

    # Save metadata in DB (no file yet — upload happens from frontend)
    new_receipt_data = ReceiptDataObject(
        user_id=current_user.id,
        store_name=data.get('store_name'),
        datetime=data.get('datetime'),
        total=data.get('total'),
        store_location=data.get('store_location'),
        payment_type=data.get('payment_type'),
        description=data.get('description'),
        category=data.get('category'),
        receipt_path=f"https://pub-{ACCOUNT_ID}.r2.dev/{object_key}"
    )
    db_session.add(new_receipt_data)
    db_session.flush()

    new_receipt = Receipt(
        receipt_id=new_receipt_data.id,
        filename=object_key,
        content_type=ext,
    )
    db_session.add(new_receipt)
    db_session.commit()

    return jsonify({
        "uploadUrl": presigned_url,
        "receiptId": new_receipt_data.id,
        "publicUrl": new_receipt_data.receipt_path
    }), 200

# -------------------------
# 2. Archive access
# -------------------------
@receipts_bp.route('/receipts-archive', methods=['GET'])
@login_required
def ReceiptsArchiveAccess():
    receipt_data_objects = db_session.query(ReceiptDataObject).filter(
        ReceiptDataObject.user_id == current_user.id
    ).all()
    serialized = [r.to_dict() for r in receipt_data_objects]
    return jsonify({'receipt_data_objects': serialized})

# -------------------------
# 3. Delete all receipts for user
# -------------------------
@receipts_bp.route("/delete-receipts", methods=["POST"])
@login_required
def delete_receipts():
    try:
        user_receipts = db_session.query(ReceiptDataObject).filter_by(
            user_id=current_user.id
        ).all()

        if not user_receipts:
            return jsonify({"message": "No receipts found for this user"}), 404

        deleted_files = []
        failed_files = []

        for rdo in user_receipts:
            try:
                if rdo.receipt:
                    s3_client.delete_object(Bucket=BUCKET_NAME, Key=rdo.receipt.filename)
                    deleted_files.append(rdo.receipt.filename)
            except Exception as e:
                print(f"Failed to delete {rdo.receipt.filename}: {e}")
                failed_files.append(rdo.receipt.filename)

            if rdo.receipt:
                db_session.delete(rdo.receipt)
            db_session.delete(rdo)

        db_session.commit()

        return jsonify({
            "message": "User receipts deleted",
            "deleted_files": deleted_files,
            "failed_files": failed_files
        })
    except Exception as e:
        print("Failed to delete:", e)
        return jsonify({'message': 'Error deleting receipts'}), 500
