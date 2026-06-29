from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, SalesOrder, Customer
from datetime import datetime, date
from sqlalchemy import func, extract

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


def parse_month(month_str):
    parts = month_str.split('-')
    return int(parts[0]), int(parts[1])


def month_range(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    month_str = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month = parse_month(month_str)
    start_date, end_date = month_range(year, month)

    monthly = db.session.query(
        func.coalesce(func.sum(SalesOrder.total_amount), 0),
        func.coalesce(func.sum(SalesOrder.gross_profit), 0)
    ).filter(
        SalesOrder.order_date >= start_date,
        SalesOrder.order_date < end_date
    ).first()

    new_customers = Customer.query.filter(
        func.date(Customer.created_at) >= start_date,
        func.date(Customer.created_at) < end_date
    ).count()

    yearly_rows = db.session.query(
        extract('month', SalesOrder.order_date).label('month'),
        func.coalesce(func.sum(SalesOrder.total_amount), 0),
        func.coalesce(func.sum(SalesOrder.gross_profit), 0)
    ).filter(
        extract('year', SalesOrder.order_date) == year
    ).group_by(
        extract('month', SalesOrder.order_date)
    ).order_by(
        extract('month', SalesOrder.order_date)
    ).all()

    monthly_cust = db.session.query(
        Customer.name,
        func.coalesce(func.sum(SalesOrder.total_amount), 0)
    ).join(
        SalesOrder, SalesOrder.customer_id == Customer.id
    ).filter(
        SalesOrder.order_date >= start_date,
        SalesOrder.order_date < end_date
    ).group_by(
        Customer.id, Customer.name
    ).order_by(
        func.sum(SalesOrder.total_amount).desc()
    ).all()

    yearly_cust = db.session.query(
        Customer.name,
        func.coalesce(func.sum(SalesOrder.total_amount), 0)
    ).join(
        SalesOrder, SalesOrder.customer_id == Customer.id
    ).filter(
        extract('year', SalesOrder.order_date) == year
    ).group_by(
        Customer.id, Customer.name
    ).order_by(
        func.sum(SalesOrder.total_amount).desc()
    ).all()

    yearly_map = {int(r[0]): r for r in yearly_rows}
    yearly_data = []
    for m in range(1, 13):
        found = yearly_map.get(m)
        yearly_data.append({
            'month': m,
            'total_amount': float(found[1]) if found else 0,
            'gross_profit': float(found[2]) if found else 0
        })

    return jsonify({
        'monthly': {
            'total_amount': float(monthly[0]),
            'gross_profit': float(monthly[1]),
            'new_customers': new_customers
        },
        'yearly': yearly_data,
        'monthly_customer_ranking': [
            {'customer_name': r[0], 'total_amount': float(r[1])}
            for r in monthly_cust
        ],
        'yearly_customer_ranking': [
            {'customer_name': r[0], 'total_amount': float(r[1])}
            for r in yearly_cust
        ]
    })
