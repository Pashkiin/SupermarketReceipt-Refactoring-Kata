from model_objects import Discount, OfferFactory, SpecialOfferType

class DiscountCalculator:
    def __init__(self, catalog, offers, bundle_offers):
        self.catalog = catalog
        self.offers = offers
        self.bundle_offers = bundle_offers
        self.offer_factory = OfferFactory()

    def calculate_discounts(self, product_quantities, coupons, current_date):
        discounts = []
        remaining_quantities = product_quantities.copy()
        
        discounts.extend(self._calculate_bundle_discounts(remaining_quantities))

        discounts.extend(self._calculate_coupon_discounts(remaining_quantities, coupons, current_date))
        
        discounts.extend(self._calculate_standard_discounts(remaining_quantities))

        return discounts
    
    def _calculate_bundle_discounts(self, remaining_quantities):
        discounts = []
        while True:
            best_offer = None
            best_savings = 0.0
            
            for bundle in self.bundle_offers:
                if bundle.can_apply_bundle(remaining_quantities):
                    savings = bundle.get_discount_amount(self.catalog)
                    if savings > best_savings:
                        best_savings = savings
                        best_offer = bundle
            
            if best_offer:
                best_offer.consume(remaining_quantities)
                discounts.append(Discount(None, best_offer.get_description(), -best_savings))
            else:
                break
        return discounts

    def _calculate_coupon_discounts(self, remaining_quantities, coupons, current_date):
        discounts = []
        for coupon in coupons:
            if not (coupon.start_date <= current_date <= coupon.end_date):
                continue
            
            if coupon.product not in remaining_quantities:
                continue

            offer = self.offer_factory.create(coupon.offer_type, coupon.product, coupon.argument)
            
            quantity = remaining_quantities[coupon.product]
            unit_price = self.catalog.unit_price(coupon.product)
            
            discount = offer.calculate_discount(quantity, unit_price)
            
            if discount:
                discounts.append(discount)
                self._consume_coupon_items(remaining_quantities, coupon, quantity)
                
        return discounts

    def _consume_coupon_items(self, remaining_quantities, coupon, current_quantity):
        if coupon.offer_type == SpecialOfferType.COUPON_DISCOUNT:
            arg = coupon.argument
            max_items_affected = arg['threshold'] + arg['limit']
            items_used = min(current_quantity, max_items_affected)
            remaining_quantities[coupon.product] -= items_used
        else:
            del remaining_quantities[coupon.product]
            
        if coupon.product in remaining_quantities and remaining_quantities[coupon.product] <= 0:
            del remaining_quantities[coupon.product]

    def _calculate_standard_discounts(self, remaining_quantities):
        discounts = []
        for product, quantity in remaining_quantities.items():
            if product in self.offers:
                offer = self.offers[product]
                unit_price = self.catalog.unit_price(product)
                discount = offer.calculate_discount(quantity, unit_price)
                if discount:
                    discounts.append(discount)
        return discounts