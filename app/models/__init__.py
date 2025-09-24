from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users' 
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(1024), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    email = Column(String)
    phone = Column(String)
    provider = Column(String)
    provider_id = Column(Integer)
    created_at = Column(DateTime)
    last_login =  Column(DateTime)
  
    tasks = relationship("Task", back_populates="user")

    # raw_material_usage_logs = relationship("RawMaterialUsageLog", back_populates='user')
    # specimen_usage_logs = relationship("SpecimenUsageLog", back_populates='user')
    
    # raw_material_purchase_logs = relationship('RawMaterialPurchaseLog', back_populates='user')
    # specimen_purchase_logs = relationship('SpecimenPurchaseLog', back_populates='user')


    # specimen_purchase_logs = relationship('SpecimenPurchaseLog', back_populates='user')

    # receipts = relationship("Receipt", back_populates='user')


    def to_dict(self):
        return{
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'email': self.email,
            'phone': self.phone,
            'provider': self.provider,
            'provider_id': self.provider_id,
            'created_at': self.created_at,
            'last_login': self.last_login,
        }
    
    def get_id(self):
        return str(self.id)
    
class RawMaterial(Base):
    __tablename__= 'raw_materials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime)

    item_usage_logs = relationship("TaskItemUsageLog", back_populates='item')

    purchase_logs = relationship('RawMaterialPurchaseLog', back_populates='item')
    
    inventory_log = relationship('RawMaterialInventoryLog', back_populates='item')

    field_recipe_item_links = relationship("FieldRecipeItemLink", back_populates="item")

    product_recipe_item_links = relationship("ProductRecipeItemLink", back_populates="item")


    def to_dict(self):
        return{
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            
        }
    
    
    def get_id(self):
        return str(self.id)

class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)

    raw_material_purchase_logs = relationship("RawMaterialPurchaseLog", back_populates='vendor')

    item_vendor_links = relationship('RawMaterialVendorLink', back_populates='vendor')

    specimen_vendor_links = relationship('SpecimenVendorLink', back_populates='vendor')

    receipts = relationship('Receipt', back_populates='vendor')

    def to_dict(self):
        return{
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'website': self.website  
        }
    
    def get_id(self):
        return str(self.id)

class RawMaterialPurchaseLog(Base):
    __tablename__ = 'raw_material_purchase_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_date = Column(String)
    purchase_date = Column(String)
    purchase_amount = Column(Float)
    purchase_unit = Column(String)
    cost = Column(Float)
    notes = Column(String)


    inventory_log_id = Column(Integer, ForeignKey('raw_material_inventory_logs.id'), nullable=False)
    inventory_log = relationship('RawMaterialInventoryLog', back_populates='purchase_logs')

    item_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
    item = relationship('RawMaterial', back_populates='purchase_logs')

    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor = relationship('Vendor', back_populates='raw_material_purchase_logs')

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='raw_material_purchase_logs')

    # receipt_entry

    def to_dict(self):
        return{
            'id': self.id,
            'log_date': self.log_date,
            'purchase_date': self.purchase_date,
            'purchase_amount': self.purchase_amount,
            'purchase_unit': self.purchase_unit,
            'cost': self.cost,
            'notes': self.notes
        }
    
    def get_id(self):
        return str(self.id)

class RawMaterialInventoryLog(Base):
    __tablename__= 'raw_material_inventory_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount_on_hand = Column(Float)
    amount_on_hand_unit = Column(String)
    periodic_auto_replace  = Column(Float)
    periodic_auto_replace_unit = Column(String)
    created_at = Column(DateTime)
    last_updated = Column(DateTime)

    item_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
    item = relationship('RawMaterial', back_populates='inventory_log')

    def to_dict(self):
        return{
           'id': self.id,
           'amount_on_hand': self.amount_on_hand,
           'amount_on_hand_unit': self.amount_on_hand_unit,
           'periodic_auto_replace': self.periodic_auto_replace,
           'periodic_auto_replace_unit': self.periodic_auto_replace_unit,
           'created_at': self.created_at,
           'last_updated': self.last_updated
        }
    
    def get_id(self):
        return str(self.id)

# class RawMaterialUsageLog(Base):
#     __tablename__ = 'raw_material_usage_logs'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     usage_amount = Column(Float)
#     usage_unit = Column(String)

#     task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
#     task = relationship('Task', back_populates='raw_material_usage_logs')

#     item_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
#     item = relationship('RawMaterial', back_populates='item_usage_logs')

#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='raw_material_usage_logs')

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'usage_amount': self.usage_amount,
#             'usage_unit': self.usage_unit
#         }
    
#     def get_id(self):
#         return str(self.id)
    
# class RawMaterialProductRecipeLink(Base):
#     __tablename__ = "raw_material_product_recipe_links"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     usage_quantity = Column(Float)
#     usage_unit = Column(String)
#     created_at = Column(DateTime)
#     last_updated = Column(DateTime)

#     product_recipe_id = Column(Integer, ForeignKey("product_recipes.id"))
#     product_recipe_ = relationship("ProductRecipe", back_populates='raw_material_product_recipe_links')

#     item_id = Column(Integer, ForeignKey("raw_materials.id"))
#     item = relationship("RawMaterial", back_populates="product_recipe_item_links")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "product_recipe_item_link": self.product_recipe_item_link,
#             "item_id": self.item_id,
#             "usage_quantity": self.usage_quantity,
#             "usage_unit": self.usage_unit,
#             "created_at": self.created_at,
#             "last_updated": self.last_updated
#         }

#     def get_id(self):
#         return str(self.id)

# class RawMaterialFieldRecipeLink(Base):
#     __tablename__ = "raw_material_field_recipe_link"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     usage_quantity = Column(Float)
#     usage_unit = Column(String)
#     created_at = Column(DateTime)
#     last_updated = Column(DateTime)

#     field_recipe_id = Column(Integer, ForeignKey("field_recipes.id"))
#     field_recipe = relationship("FieldRecipe", back_populates='raw_materialfield_recipe_links')

#     item_id = Column(Integer, ForeignKey("raw_materials.id"))
#     item = relationship("RawMaterial", back_populates="field_recipe_item_links")


#     def to_dict(self):
#         return {
#             "id": self.id,
#             "field_recipe_item_link": self.field_recipe_item_link,
#             "item_id": self.item_id,
#             "usage_quantity": self.usage_quantity,
#             "usage_unit": self.usage_unit,
#             "created_at": self.created_at,
#             "last_updated": self.last_updated
#         }

#     def get_id(self):
#         return str(self.id)

# class Specimen(Base):
#     __tablename__ = 'specimen'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String)
#     created_at = Column(DateTime)
#     species = Column(DateTime)

#     # purchase_logs = relationship('RawMaterialPurchaseLog', back_populates='specimen')


#     specimen_vendor_links = relationship('SpecimenVendorLink', back_populates='specimen')

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'name': self.name,
#             'created_at': self.created_at
#         }
    
#     def get_id(self):
#         return str(self.id)

# class SpecimenPurchaseLog(Base):
#     __tablename__ = 'specimen_purchase_logs'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     log_date = Column(String)
#     purchase_date = Column(String)
#     purchase_amount = Column(Float)
#     purchase_unit = Column(String)
#     cost = Column(Float)
#     notes = Column(String)

#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='specimen_purchase_logs')

#     specimen_id = ()

#     vendor_id = ()

#     inventory_log = ()

#     purchase_log_vendor_link_id = Column(Integer, ForeignKey('specimen_vendor_links.id'), nullable=False)
#     purchase_log_vendor_link = relationship('SpecimenVendorLink', back_populates='purchase_logs')

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'log_date': self.log_date,
#             'purchase_date': self.purchase_date,
#             'purchase_amount': self.purchase_amount,
#             'purchase_unit': self.purchase_unit,
#             'cost': self.cost,
#             'notes': self.notes
#         }
    
#     def get_id(self):
#         return str(self.id) 

# class SpecimenInventoryLog(Base):
#     __tablename__= 'specimen_inventory_logs'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     amount_on_hand = Column(Float)
#     amount_on_hand_unit = Column(String)
#     periodic_auto_replace  = Column(Float)
#     periodic_auto_replace_unit = Column(String)
#     created_at = Column(DateTime)
#     last_updated = Column(DateTime)


#     item_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
#     item = relationship('RawMaterial', back_populates='inventory_log')

#     def to_dict(self):
#         return{
#            'id': self.id,
#            'amount_on_hand': self.amount_on_hand,
#            'amount_on_hand_unit': self.amount_on_hand_unit,
#            'periodic_auto_replace': self.periodic_auto_replace,
#            'periodic_auto_replace_unit': self.periodic_auto_replace_unit,
#            'created_at': self.created_at,
#            'last_updated': self.last_updated
#         }
    
#     def get_id(self):
#         return str(self.id)

# class SpecimenUsageLog(Base):
#     __tablename__ = 'specimen_usage_logs'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     usage_amount = Column(Float)
#     usage_unit = Column(String)

#     task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
#     task = relationship('Task', back_populates='item_usage_logs')

#     specimen_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
#     specimen = relationship('RawMaterial', back_populates='item_usage_logs')

#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='item_usage_logs')

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'usage_amount': self.usage_amount,
#             'usage_unit': self.usage_unit
#         }
    
#     def get_id(self):
#         return str(self.id)
    
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    total_time = Column(Float)
    memo = Column(String)
    #priority = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="tasks")

    # raw_material_usage_logs = relationship('RawMaterialUsageLog', back_populates='task')
    # specimen_usage_logs = relationship('SpecimenUsageLog', back_populates='task')

    def to_dict(self):
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'total_time': self.total_time,
            'memo': self.memo
        }
    
    def get_id(self):
        return str(self.id)


# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String)
#     description = Column(String)
#     created_at = Column(DateTime)

#     product_recipe_link = relationship("ProductRecipeLink", back_populates="product")

#     product_batch_links = relationship("ProductBatchLink", back_populates="product")

#     def to_dict(self):
#         return {
#             'id': self.id,
#             "name": self.name,
#             "description": self.description,
#             "created_at": self.created_at,
#         }

#     def get_id(self):
#         return str(self.id)

# class ProductRecipe(Base):
#     __tablename__ = "product_recipes"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String)
#     created_at = Column(DateTime)
#     last_updated = Column(DateTime)
#     cost = Column(Float)

#     raw_material_product_recipe_link = relationship("RawMaterialProductRecipeLink", back_populates="product_recipe")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "created_at": self.created_at,
#             "last_update": self.last_update,
#             "cost": self.cost,
#         }

#     def get_id(self):
#         return str(self.id)

# class ProductBatch(Base):
#     __tablename__ = "product_batches"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     production_date = Column(DateTime)
#     created_at = Column(DateTime)
#     quantity = Column(Float)
#     msrp = Column(Float)

#     product_batch_link = relationship("ProductBatchLink", back_populates="product_batch")

#     def to_dict(self):
#         return {
#             'id': self.id,
#             "prodution_date": self.prodution_date,
#             "created_at": self.created_at,
#             "quantity": self.quantity,
#             "msrp": self.msrp
#         }
    
#     def get_id(self):
#         return str(self.id)

# class ProductBatchLink(Base):
#     __tablename__ = 'product_batch_links'
#     id = Column(Integer, primary_key=True, autoincrement=True)
    
#     product_id = Column(Integer, ForeignKey('products.id'))
#     product = relationship("Product", back_populates='product_batch_links')
    
#     product_batch_id = Column(Integer, ForeignKey('product_batches.id'))
#     product_batch = relationship("ProductBatch", back_populates="product_batch_link")

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'product_id': self.product_id,
#             'product_batch_id': self.product_batch_id
#         }
    
#     def get_id(self):
#         return str(self.id)
    
# class Field(Base):
#     __tablename__ = "fields"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     created_at = Column(DateTime)
#     weight_q = Column(Float)
#     weight_u = Column(String)
#     volume_q = Column(Float)
#     volume_u = Column(String)
#     description = Column(String)
#     memo = Column(String)
#     contaminated = Column(Boolean)
#     inoculated = Column(Boolean)
#     contamination_log_date = (DateTime)
#     inoculation_log_date = (DateTime)

#     field_recipe_link = relationship("FieldRecipeLink", back_populates="field")

#     field_batch_link = relationship("FieldBatchLink", back_populates="field")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "created_at": self.created_at,
#             "weight_q": self.weight_q,
#             "weight_u": self.weight_u,
#             "volume_q": self.volume_q,
#             "volume_u": self.volume_u,
#             "description": self.description,
#             "memo": self.memo,
#             "contaminated": self.contaminated,
#             "inoculated": self.inoculated,
#             "contamination_log_date": self.contamination_log_date,
#             "inoculation_log_date": self.inoculation_log_date
#         }
    
#     def get_id(self):
#         return str(self.id)
    
# class FieldRecipe(Base):
#     __tablename__ = "field_recipes"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String)
#     created_at = Column(DateTime)
#     last_updated = Column(DateTime)
#     cost = Column(Float)
    
#     field_recipe_link = relationship("FieldRecipeLink", back_populates="field_recipe")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "created_at": self.created_at,
#             "last_updated": self.last_updated,
#         }

#     def get_id(self):
#         return str(self.id)

# class FieldBatch(Base):
#     __tablename__ = "field_batches"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     production_date = Column(DateTime)
#     created_at = Column(DateTime)
#     quantity = Column(Float)

#     field_batch_links = relationship("FieldBatchLink", back_populates='field_batches')

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'production_date': self.production_date,
#             'created_at': self.created_at,
#             'quantity': self.quantity,
#         }
    
#     def get_id(self):
#         return str(self.id)

# class FieldBatchLink(Base):
#     __tablename__ = 'field_batch_links'
#     id = Column(Integer, primary_key=True, autoincrement=True)
    
#     field_id = Column(Integer, ForeignKey('fields.id'))
#     field = relationship("Field", back_populates='field_batch_link')
    
#     field_batch_id = Column(Integer, ForeignKey('field_batches.id'))
#     field_batches = relationship("FieldBatch", back_populates="field_batch_links")

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'field_id': self.field_id,
#             'field_batch_id': self.field_batch_id
#         }
    
#     def get_id(self):
#         return str(self.id)

class ReceiptEntry(Base):
    __tablename__ = "receipt_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime)
    image_path = Column(String)
    created_at = Column(DateTime)
    memo = Column(String)

    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    vendor = relationship("Vendor", back_populates='receipts')

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates='receipts')

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "image_path": self.image_path,
            "created_at": self.created_at,
            "memo": self.memo,
            "vendor_id": self.vendor_id,
            "user_id": self.user_id,
        }

    def get_id(self):
        return str(self.id)

