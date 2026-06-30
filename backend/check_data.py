from app import app
from models import db, SalesOrderSupplier, PurchaseOrder

with app.app_context():
    # Check SalesOrderSupplier records for orders corresponding to PO IDs 2,4,14,18,etc.
    # PO 2 = PO2026062969A56F-2 → sales order PO2026062969A56F
    # PO 4 = SO2026062900FEB3-2  → sales order SO2026062900FEB3
    po_ids_with_issues = [2, 4, 14, 18, 22, 26, 30, 33]
    for po_id in po_ids_with_issues:
        po = PurchaseOrder.query.get(po_id)
        if po:
            print(f'\nPO ID={po.id} order_no={po.order_no}')
            # Get the sales order no from the remark
            remark = po.remark or ''
            so_no = remark.replace('由销售订单 ', '').replace(' 自动生成', '') if '由销售订单' in remark else ''
            print(f'  Remark: {remark}')
            print(f'  SO No: {so_no}')
            if so_no:
                # Find SalesOrderSupplier records for this SO
                from models import SalesOrder
                so = SalesOrder.query.filter_by(order_no=so_no).first()
                if so:
                    print(f'  SO ID: {so.id}')
                    sups = SalesOrderSupplier.query.filter_by(order_id=so.id).all()
                    print(f'  Supplier records: {len(sups)}')
                    for s in sups:
                        print(f'    supplier="{s.supplier}" product="{s.product}" qty={s.quantity} price={s.price}')
    print('\n\nAll SalesOrderSupplier records:')
    for s in SalesOrderSupplier.query.all():
        print(f'  ID={s.id} order_id={s.order_id} supplier="{s.supplier}" product="{s.product}" qty={s.quantity} price={s.price}')
