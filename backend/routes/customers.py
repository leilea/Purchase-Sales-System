from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer

bp = Blueprint('customers', __name__)


def generate_customer_code():
    today = date.today()
    prefix = today.strftime('%y%m%d')
    last = Customer.query.filter(
        Customer.code.like(f'{prefix}%')
    ).order_by(Customer.code.desc()).first()
    if last:
        seq = int(last.code[-3:]) + 1
    else:
        seq = 1
    return f'{prefix}{seq:03d}'


def serialize_customer(c):
    return {
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'level': c.level,
        'contact': c.contact,
        'phone': c.phone,
        'address': c.address,
        'company_name': c.company_name,
        'tax_id': c.tax_id,
        'bank_name': c.bank_name,
        'bank_account': c.bank_account,
        'invoice_type': c.invoice_type,
        'status': c.status,
        'created_at': c.created_at.isoformat() if c.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', type=int)
    name = request.args.get('name', '')
    contact = request.args.get('contact', '')
    phone = request.args.get('phone', '')

    query = Customer.query
    if search:
        query = query.filter(db.or_(
            Customer.name.like(f'%{search}%'),
            Customer.code.like(f'%{search}%'),
            Customer.company_name.like(f'%{search}%'),
            Customer.contact.like(f'%{search}%')
        ))
    if name:
        query = query.filter(Customer.name.like(f'%{name}%'))
    if contact:
        query = query.filter(Customer.contact.like(f'%{contact}%'))
    if phone:
        query = query.filter(Customer.phone.like(f'%{phone}%'))
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(Customer.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [serialize_customer(c) for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/code', methods=['GET'])
@jwt_required()
def next_code():
    return jsonify({'code': generate_customer_code()})


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify(serialize_customer(customer))


@bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json()

    code = data.get('code') or generate_customer_code()
    if Customer.query.filter_by(code=code).first():
        return jsonify({'error': 'Customer code already exists'}), 400

    customer = Customer(
        code=code,
        name=data.get('name'),
        level=data.get('level', 'A级'),
        contact=data.get('contact'),
        phone=data.get('phone'),
        address=data.get('address', ''),
        company_name=data.get('company_name', ''),
        tax_id=data.get('tax_id', ''),
        bank_name=data.get('bank_name', ''),
        bank_account=data.get('bank_account', ''),
        invoice_type=data.get('invoice_type', ''),
        status=data.get('status', 1)
    )
    db.session.add(customer)
    db.session.commit()

    return jsonify(serialize_customer(customer)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()

    if data.get('name'):
        customer.name = data['name']
    if 'level' in data:
        customer.level = data['level']
    if 'contact' in data:
        customer.contact = data['contact']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    if 'company_name' in data:
        customer.company_name = data['company_name']
    if 'tax_id' in data:
        customer.tax_id = data['tax_id']
    if 'bank_name' in data:
        customer.bank_name = data['bank_name']
    if 'bank_account' in data:
        customer.bank_account = data['bank_account']
    if 'invoice_type' in data:
        customer.invoice_type = data['invoice_type']
    if 'status' in data:
        customer.status = data['status']

    db.session.commit()
    return jsonify(serialize_customer(customer))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})
