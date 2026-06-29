from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Invoice
from datetime import datetime

bp = Blueprint('invoices', __name__)


def serialize(inv):
    return {
        'id': inv.id,
        'order_no': inv.order_no,
        'total_amount': float(inv.total_amount) if inv.total_amount else 0,
        'customer_name': inv.customer_name,
        'tax_id': inv.tax_id,
        'invoice_type': inv.invoice_type,
        'invoice_amount': float(inv.invoice_amount) if inv.invoice_amount else 0,
        'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else None,
        'attachment': inv.attachment,
        'remark': inv.remark,
        'created_at': inv.created_at.isoformat() if inv.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_invoices():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    order_no = request.args.get('order_no', '')
    customer_name = request.args.get('customer_name', '')
    total_amount_min = request.args.get('total_amount_min', type=float)
    total_amount_max = request.args.get('total_amount_max', type=float)

    query = Invoice.query
    if order_no:
        query = query.filter(Invoice.order_no.like(f'%{order_no}%'))
    if customer_name:
        query = query.filter(Invoice.customer_name.like(f'%{customer_name}%'))
    if total_amount_min is not None:
        query = query.filter(Invoice.total_amount >= total_amount_min)
    if total_amount_max is not None:
        query = query.filter(Invoice.total_amount <= total_amount_max)

    pagination = query.order_by(Invoice.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [serialize(i) for i in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    data = request.get_json()

    invoice = Invoice(
        order_no=data.get('order_no', ''),
        total_amount=data.get('total_amount', 0),
        customer_name=data.get('customer_name'),
        tax_id=data.get('tax_id'),
        invoice_type=data.get('invoice_type'),
        invoice_amount=data.get('invoice_amount', 0),
        invoice_date=datetime.strptime(data['invoice_date'], '%Y-%m-%d').date() if data.get('invoice_date') else None,
        attachment=data.get('attachment'),
        remark=data.get('remark')
    )
    db.session.add(invoice)
    db.session.commit()

    return jsonify(serialize(invoice)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    data = request.get_json()

    if 'order_no' in data:
        invoice.order_no = data['order_no']
    if 'total_amount' in data:
        invoice.total_amount = data['total_amount']
    if 'customer_name' in data:
        invoice.customer_name = data['customer_name']
    if 'tax_id' in data:
        invoice.tax_id = data['tax_id']
    if 'invoice_type' in data:
        invoice.invoice_type = data['invoice_type']
    if 'invoice_amount' in data:
        invoice.invoice_amount = data['invoice_amount']
    if 'invoice_date' in data:
        invoice.invoice_date = datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
    if 'attachment' in data:
        invoice.attachment = data['attachment']
    if 'remark' in data:
        invoice.remark = data['remark']

    db.session.commit()
    return jsonify(serialize(invoice))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({'message': 'Invoice deleted successfully'})
