import datetime

from model_objects import OfferFactory, BundleOffer
from receipt import Receipt
from discount_calculator import DiscountCalculator
from loyalty_service import LoyaltyService

class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.bundle_offers = []
        self.offer_factory = OfferFactory()
        self.loyalty_service = LoyaltyService()

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = self.offer_factory.create(offer_type, product, argument)

    def add_bundle_offer(self, bundle_products, discount_percentage):
        self.bundle_offers.append(BundleOffer(bundle_products, discount_percentage))

    def checks_out_articles_from(self, the_cart, current_date=None, available_points=0):
        if current_date is None:
            current_date = datetime.date.today()

        receipt = Receipt()

        self._add_items_to_receipt(receipt, the_cart)
        self._apply_discounts(receipt, the_cart, current_date)
        self.loyalty_service.apply_reduction(receipt, available_points)
        self.loyalty_service.calculate_points_earned(receipt)

        return receipt

    def _add_items_to_receipt(self, receipt, cart):
        for item in cart.items:
            unit_price = self.catalog.unit_price(item.product)
            price = item.quantity * unit_price
            receipt.add_product(item.product, item.quantity, unit_price, price)

    def _apply_discounts(self, receipt, cart, current_date):
        calculator = DiscountCalculator(self.catalog, self.offers, self.bundle_offers)
        discounts = calculator.calculate_discounts(
            cart.product_quantities, 
            cart.coupons, 
            current_date
        )
        for discount in discounts:
            receipt.add_discount(discount)
