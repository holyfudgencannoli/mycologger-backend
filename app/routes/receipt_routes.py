from flask import Blueprint, jsonify, request, session
from datetime import datetime
from ..db import db_session
from ..models import ReceiptEntry, User
import os
import boto3
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from flask_jwt_extended  import jwt_required, get_jwt_identity

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET")


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
@receipts_bp.route('/get-signed-upload-url', methods=['POST'])
@jwt_required()
def get_upload_url():
    """Generate a presigned URL so frontend can upload directly to R2"""
    data = request.get_json()
    filename = data.get("filename")

    user_id = get_jwt_identity()

    if not filename:
        return jsonify({"error": "Missing filename"}), 400
    
    content_type = data.get("content_type")
    print(content_type)

    # Secure + unique filename (user_id + timestamp + ext)
    ext = os.path.splitext(filename)[1].lower()
    safe_name = secure_filename(filename)
    object_key = f"user_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
    receipt_path=f"https://pub-{ACCOUNT_ID}.r2.dev/{object_key}"

    # Presigned URL for direct upload
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": BUCKET_NAME, "Key": object_key, "ContentType": content_type},
        ExpiresIn=300,  # 5 minutes
        HttpMethod="PUT"
    )

    return jsonify({
        "uploadUrl": presigned_url,
        "fileKey": object_key,
        "publicUrl": receipt_path
    }), 200

# -------------------------
# 2. Archive access
# # -------------------------
# @receipts_bp.route('/receipts-archive', methods=['GET'])
# @jwt_required()
# def ReceiptsArchiveAccess():
#     receipt_data_objects = db_session.query(ReceiptDataObject).filter(
#         ReceiptDataObject.user_id == current_user.id
#     ).all()
#     serialized = [r.to_dict() for r in receipt_data_objects]
#     return jsonify({'receipt_data_objects': serialized})

# -------------------------
# 3. Delete all receipts for user
# -------------------------
# @receipts_bp.route("/delete-receipts", methods=["POST"])
# @jwt_required()
# def delete_receipts():
#     try:
#         user_receipts = db_session.query(ReceiptDataObject).filter_by(
#             user_id=current_user.id
#         ).all()

#         if not user_receipts:
#             return jsonify({"message": "No receipts found for this user"}), 404

#         deleted_files = []
#         failed_files = []

#         for rdo in user_receipts:
#             try:
#                 if rdo.receipt:
#                     s3_client.delete_object(Bucket=BUCKET_NAME, Key=rdo.receipt.filename)
#                     deleted_files.append(rdo.receipt.filename)
#             except Exception as e:
#                 print(f"Failed to delete {rdo.receipt.filename}: {e}")
#                 failed_files.append(rdo.receipt.filename)

#             if rdo.receipt:
#                 db_session.delete(rdo.receipt)
#             db_session.delete(rdo)

#         db_session.commit()

#         return jsonify({
#             "message": "User receipts deleted",
#             "deleted_files": deleted_files,
#             "failed_files": failed_files
#         })
#     except Exception as e:
#         print("Failed to delete:", e)
#         return jsonify({'message': 'Error deleting receipts'}), 500
