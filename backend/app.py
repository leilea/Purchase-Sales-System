import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from config import SECRET_KEY, DATABASE_PATH, JWT_EXPIRATION_HOURS
from models import db

jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=JWT_EXPIRATION_HOURS)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f'[JWT Invalid] {error}')
        return jsonify({'error': f'Invalid token: {str(error)}'}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        print(f'[JWT Unauthorized] {error}')
        return jsonify({'error': f'Missing token: {str(error)}'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f'[JWT Expired] header={jwt_header}')
        return jsonify({'error': 'Token has expired'}), 401

    from routes import auth, products, suppliers, customers, purchases, sales, inventory, categories, units, dashboard, invoices
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(products.bp, url_prefix='/api/products')
    app.register_blueprint(suppliers.bp, url_prefix='/api/suppliers')
    app.register_blueprint(customers.bp, url_prefix='/api/customers')
    app.register_blueprint(purchases.bp, url_prefix='/api/purchases')
    app.register_blueprint(sales.bp, url_prefix='/api/sales')
    app.register_blueprint(inventory.bp, url_prefix='/api/inventory')
    app.register_blueprint(categories.bp, url_prefix='/api/categories')
    app.register_blueprint(units.bp, url_prefix='/api/units')
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(invoices.bp, url_prefix='/api/invoices')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'PSS管理系统 API'})

    with app.app_context():
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        db.create_all()
        _migrate_db()
        _create_default_admin()

    return app


def _migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    
    # Product new columns
    for col in ['spec', 'material_grade', 'surface_treatment']:
        if col not in [c['name'] for c in inspector.get_columns('products')]:
            db.session.execute(text(f'ALTER TABLE products ADD COLUMN {col} VARCHAR(200)'))
    
    # SalesOrder new columns
    for col, typ in [('address', 'TEXT'), ('freight', 'NUMERIC(10,2) DEFAULT 0'), ('invoice_required', 'INTEGER DEFAULT 0'), ('gross_profit', 'NUMERIC(10,2) DEFAULT 0')]:
        if col not in [c['name'] for c in inspector.get_columns('sales_orders')]:
            db.session.execute(text(f'ALTER TABLE sales_orders ADD COLUMN {col} {typ}'))
    
    # SalesOrderItem new columns
    for col, typ in [('spec', 'VARCHAR(200)'), ('material_grade', 'VARCHAR(100)'), ('surface_treatment', 'VARCHAR(200)'), ('matching', 'VARCHAR(100)'), ('package_quantity', 'NUMERIC(10,2) DEFAULT 0'), ('package_count', 'NUMERIC(10,2) DEFAULT 0'), ('remark', 'TEXT')]:
        if col not in [c['name'] for c in inspector.get_columns('sales_order_items')]:
            db.session.execute(text(f'ALTER TABLE sales_order_items ADD COLUMN {col} {typ}'))
    
    # PurchaseOrderItem new columns
    for col, typ in [('spec', 'VARCHAR(200)'), ('grade', 'VARCHAR(100)'), ('surface_treatment', 'VARCHAR(200)'), ('total_weight', 'NUMERIC(10,3) DEFAULT 0'), ('unit_weight', 'NUMERIC(10,4) DEFAULT 0'), ('packaging', 'VARCHAR(200)'), ('tax', 'NUMERIC(10,2) DEFAULT 0')]:
        if col not in [c['name'] for c in inspector.get_columns('purchase_order_items')]:
            db.session.execute(text(f'ALTER TABLE purchase_order_items ADD COLUMN {col} {typ}'))

    # Create new tables if not exist
    for table_name in ['sales_order_suppliers', 'sales_order_logistics']:
        if table_name not in inspector.get_table_names():
            db.create_all()
            break
    
    db.session.commit()


def _create_default_admin():
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            nickname='Administrator',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()


app = create_app()

if __name__ == '__main__':
    import re
    import sys
    from pathlib import Path
    from werkzeug.serving import run_simple

    backend_dir = Path(__file__).parent
    extra = {str(p) for p in backend_dir.rglob('*.py')}
    site_pkgs = re.escape(str(Path(sys.base_prefix) / 'Lib' / 'site-packages'))
    run_simple(
        '127.0.0.1', 5000, app,
        use_reloader=True,
        use_debugger=True,
        extra_files=list(extra),
        exclude_patterns=[site_pkgs + re.escape('\\') + '.*'],
    )
