from model_objects import Discount

class DiscountCalculator:
    def __init__(self, catalog, offers, bundle_offers):
        self.catalog = catalog
        self.offers = offers
        self.bundle_offers = bundle_offers

    def calculate_discounts(self, product_quantities):
        discounts = []
        remaining_quantities = product_quantities.copy()
        
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
                discounts.append(Discount(
                    product=None, 
                    description=best_offer.get_description(), 
                    discount_amount=-best_savings
                ))
            else:
                break
        
        for product, quantity in remaining_quantities.items():
            if product in self.offers:
                offer = self.offers[product]
                unit_price = self.catalog.unit_price(product)
                discount = offer.calculate_discount(quantity, unit_price)
                if discount:
                    discounts.append(discount)
                    
        return discounts