from app import app
from models import db, SalesOrderSupplier, Supplier, PurchaseOrder, PurchaseOrderItem

with app.app_context():
    print("=== Checking PO ID=33 ===")
    po = PurchaseOrder.query.get(33)
    print(f'PO 33: {po.order_no} items={po.items.count()}')
    
    from models import SalesOrder
    so_no = po.remark.replace('由销售订单 ', '').replace(' 自动生成', '') if po.remark and '自动生成' in po.remark else ''
    if so_no:
        so = SalesOrder.query.filter_by(order_no=so_no).first()
        if so:
            sups = SalesOrderSupplier.query.filter_by(order_id=so.id).all()
            print(f'SO ID={so.id} {so_no}: {len(sups)} supplier records')
            for s in sups:
                print(f'  supplier="{s.supplier}" product="{s.product}" qty={s.quantity} price={s.price}')
    
    print("\n=== All PO items for SO202606298D5DCE ===")
    for o in PurchaseOrder.query.filter(PurchaseOrder.order_no.like('SO202606298D5DCE%')).all():
        print(f'PO {o.id}: {o.order_no} total={o.total_amount}')
        for i in o.items:
            print(f'  Item {i.id}: product_id={i.product_id} qty={i.quantity} price={i.unit_price} amount={i.amount}')
    
    print("\n=== All Suppliers ===")
    for s in Supplier.query.all():
        print(f'  ID={s.id} name="{s.name}"')
    
    print("\n=== Items in PO ID=32 ===")
    po32 = PurchaseOrder.query.get(32)
    if po32:
        for i in po32.items:
            print(f'  Item {i.id}: product_id={i.product_id} qty={i.quantity} price={i.unit_price} amount={i.amount}')
