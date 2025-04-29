# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Product, StockMovement, ProductionOrder, BillOfMaterials, QualityControl

class ProductService:
    @staticmethod
    def create_product(data):
        with transaction.atomic():
            product = Product.objects.create(**data)
            return product

    @staticmethod
    def update_stock_quantity(product_id, quantity, movement_type, reference, user):
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product_id)
            
            if movement_type == 'out' and product.stock_quantity < quantity:
                raise ValidationError(_('Yetersiz stok miktarı'))
            
            if movement_type == 'in':
                product.stock_quantity += quantity
            elif movement_type == 'out':
                product.stock_quantity -= quantity
            
            product.save()
            
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                unit_price=product.unit_price,
                reference=reference,
                created_by=user
            )
            
            return product

class ProductionService:
    @staticmethod
    def create_production_order(data, user):
        with transaction.atomic():
            # Ürün ağacını kontrol et
            product = data['product']
            quantity = data['quantity']
            bom_items = BillOfMaterials.objects.filter(product=product, is_active=True)
            
            # Malzeme yeterliliğini kontrol et
            for bom_item in bom_items:
                required_quantity = bom_item.quantity * quantity
                if bom_item.component.stock_quantity < required_quantity:
                    raise ValidationError(
                        _('Yetersiz malzeme: %(component)s (Gereken: %(required)s, Mevcut: %(available)s)'),
                        params={
                            'component': bom_item.component.name,
                            'required': required_quantity,
                            'available': bom_item.component.stock_quantity
                        }
                    )
            
            # Üretim emrini oluştur
            data['created_by'] = user
            production_order = ProductionOrder.objects.create(**data)
            
            return production_order

    @staticmethod
    def update_production_status(order_id, new_status, user):
        with transaction.atomic():
            order = ProductionOrder.objects.select_for_update().get(id=order_id)
            
            if new_status == 'completed':
                # Üretilen ürünü stoka ekle
                ProductService.update_stock_quantity(
                    product_id=order.product.id,
                    quantity=order.quantity,
                    movement_type='in',
                    reference=f'Üretim Emri #{order.order_number}',
                    user=user
                )
                
                # Kullanılan malzemeleri stoktan düş
                bom_items = BillOfMaterials.objects.filter(product=order.product, is_active=True)
                for bom_item in bom_items:
                    ProductService.update_stock_quantity(
                        product_id=bom_item.component.id,
                        quantity=bom_item.quantity * order.quantity,
                        movement_type='out',
                        reference=f'Üretim Emri #{order.order_number}',
                        user=user
                    )
            
            order.status = new_status
            order.save()
            
            return order

class QualityControlService:
    @staticmethod
    def create_quality_control(data, user):
        with transaction.atomic():
            data['inspector'] = user
            quality_control = QualityControl.objects.create(**data)
            
            # Kalite kontrol sonucuna göre üretim emrini güncelle
            if quality_control.result == 'failed':
                production_order = quality_control.production_order
                production_order.status = 'cancelled'
                production_order.save()
            
            return quality_control 