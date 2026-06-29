from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')


class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    products = db.relationship('Product', backref='unit', lazy='dynamic')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'))
    spec = db.Column(db.String(200))
    material_grade = db.Column(db.String(100))
    surface_treatment = db.Column(db.String(200))
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    sale_price = db.Column(db.Numeric(10, 2), default=0)
    stock_min = db.Column(db.Integer, default=0)
    stock_max = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inventory = db.relationship('Inventory', backref='product', uselist=False, lazy=True)
    purchase_items = db.relationship('PurchaseOrderItem', backref='product', lazy='dynamic')
    sales_items = db.relationship('SalesOrderItem', backref='product', lazy='dynamic')
    inventory_logs = db.relationship('InventoryLog', backref='product', lazy='dynamic')


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), default='A级')
    contact = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255))
    company_name = db.Column(db.String(200))
    tax_id = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    invoice_type = db.Column(db.String(50))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    order_date = db.Column(db.Date, default=datetime.utcnow().date)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='draft')
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('PurchaseOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='purchase_orders')


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Numeric(10, 2), default=0)
    unit_price = db.Column(db.Numeric(10, 2), default=0)
    amount = db.Column(db.Numeric(10, 2), default=0)


class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    business_manager = db.Column(db.String(100))
    business_manager_phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    freight_responsible = db.Column(db.String(50))
    freight = db.Column(db.Numeric(10, 2), default=0)
    payment_method = db.Column(db.String(100))
    invoice_required = db.Column(db.Integer, default=0)
    invoice_tax_rate = db.Column(db.String(20))
    order_date = db.Column(db.Date, default=datetime.utcnow().date)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    gross_profit = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='draft')
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SalesOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    suppliers = db.relationship('SalesOrderSupplier', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    logistics = db.relationship('SalesOrderLogistics', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='sales_orders')


class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    spec = db.Column(db.String(200))
    material_grade = db.Column(db.String(100))
    surface_treatment = db.Column(db.String(200))
    matching = db.Column(db.String(100))
    package_quantity = db.Column(db.Numeric(10, 2), default=0)
    package_count = db.Column(db.Numeric(10, 2), default=0)
    quantity = db.Column(db.Numeric(10, 2), default=0)
    unit_price = db.Column(db.Numeric(10, 2), default=0)
    amount = db.Column(db.Numeric(10, 2), default=0)
    remark = db.Column(db.Text)


class SalesOrderSupplier(db.Model):
    __tablename__ = 'sales_order_suppliers'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    supplier = db.Column(db.String(200))
    product = db.Column(db.String(200))
    spec = db.Column(db.String(200))
    grade = db.Column(db.String(100))
    surface_treatment = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(10, 2), default=0)
    total_weight = db.Column(db.Numeric(10, 3), default=0)
    unit_weight = db.Column(db.Numeric(10, 4), default=0)
    price = db.Column(db.Numeric(10, 2), default=0)
    packaging = db.Column(db.String(200))
    tax = db.Column(db.Numeric(10, 2), default=0)


class SalesOrderLogistics(db.Model):
    __tablename__ = 'sales_order_logistics'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    company = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    transport_status = db.Column(db.String(100))
    freight = db.Column(db.Numeric(10, 2), default=0)
    forklift_fee = db.Column(db.Numeric(10, 2), default=0)
    other_fee = db.Column(db.Numeric(10, 2), default=0)
    remark = db.Column(db.Text)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    customer_name = db.Column(db.String(200))
    tax_id = db.Column(db.String(50))
    invoice_type = db.Column(db.String(50))
    invoice_amount = db.Column(db.Numeric(10, 2), default=0)
    invoice_date = db.Column(db.Date)
    attachment = db.Column(db.String(500))
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), unique=True)
    quantity = db.Column(db.Numeric(10, 2), default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    change_type = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(10, 2))
    order_no = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
