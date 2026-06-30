from app import app
from models import db, PurchaseOrder, PurchaseOrderItem
import json

with app.app_context():
    # Check serialized output for ALL orders, specifically for total_amount display issues
    for po in PurchaseOrder.query.all():
        try:
            tv = float(po.total_amount)
        except:
            tv = None
        
        items_data = []
        for i in po.items:
            items_data.append({
                'id': i.id,
                'product_id': i.product_id,
                'quantity': float(i.quantity) if i.quantity else 0,
                'unit_price': float(i.unit_price) if i.unit_price else 0,
                'amount': float(i.amount) if i.amount else 0
            })
        
        print(f'PO {po.id}: {po.order_no} total_amount={tv} items={len(items_data)}')
        
        # Check if any item has missing amounts
        for item in items_data:
            if item['amount'] == 0 and (item['quantity'] > 0 or item['unit_price'] > 0):
                print(f'  >>> ANOMALY: Item {item["id"]} has zero amount but non-zero qty({item["quantity"]}) or price({item["unit_price"]})')
