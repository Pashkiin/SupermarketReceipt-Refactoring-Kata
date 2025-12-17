from enum import Enum
import math
from abc import ABC, abstractmethod

LOYALTY_POINT_VALUE = 0.10

class Product:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit


class ProductQuantity:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity


class ProductUnit(Enum):
    EACH = 1
    KILO = 2


class SpecialOfferType(Enum):
    THREE_FOR_TWO = 1
    TEN_PERCENT_DISCOUNT = 2
    TWO_FOR_AMOUNT = 3
    FIVE_FOR_AMOUNT = 4
    COUPON_DISCOUNT = 5

class Discount:
    def __init__(self, product, description, discount_amount):
        self.product = product
        self.description = description
        self.discount_amount = discount_amount

class Coupon:
    def __init__(self, product, code, start_date, end_date, offer_type, argument):
        self.product = product
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.offer_type = offer_type
        self.argument = argument

class Offer(ABC):
    def __init__(self, product, argument):
        self.product = product
        self.argument = argument

    @abstractmethod
    def calculate_discount(self, quantity, unit_price):
        pass


class ThreeForTwoOffer(Offer):
    def calculate_discount(self, quantity, unit_price):
        quantity_as_int = int(quantity)
        if quantity_as_int <= 2:
            return None
        discount_amount = quantity * unit_price - (
            (math.floor(quantity_as_int / 3) * 2 * unit_price) + quantity_as_int % 3 * unit_price)
        return Discount(self.product, "3 for 2", -discount_amount)


class TenPercentDiscountOffer(Offer):
    def calculate_discount(self, quantity, unit_price):
        discount_amount = quantity * unit_price * self.argument / 100.0
        return Discount(self.product, str(self.argument) + "% off", -discount_amount)


class TwoForAmountOffer(Offer):
    def calculate_discount(self, quantity, unit_price):
        quantity_as_int = int(quantity)
        if quantity_as_int < 2:
            return None
        total = self.argument * math.floor(quantity_as_int / 2) + quantity_as_int % 2 * unit_price
        discount_n = unit_price * quantity - total
        return Discount(self.product, "2 for " + str(self.argument), -discount_n)


class FiveForAmountOffer(Offer):
    def calculate_discount(self, quantity, unit_price):
        quantity_as_int = int(quantity)
        if quantity_as_int < 5:
            return None
        discount_total = unit_price * quantity - (
            self.argument * math.floor(quantity_as_int / 5) + quantity_as_int % 5 * unit_price)
        return Discount(self.product, "5 for " + str(self.argument), -discount_total)
    
class CouponDiscountOffer(Offer):    
    def calculate_discount(self, quantity, unit_price):
        arg = self.argument
        threshold = arg['threshold']
        limit = arg['limit']
        percent = arg['percent']

        quantity_as_int = int(quantity)
        
        if quantity_as_int <= threshold:
            return None
            
        discountable_items = min(quantity_as_int - threshold, limit)
        discount_amount = discountable_items * unit_price * (percent / 100.0)
        
        return Discount(self.product, f"Coupon {percent}% off next {limit} items", -discount_amount)
    
class OfferFactory:
    def create(self, offer_type, product, argument):
        if offer_type == SpecialOfferType.THREE_FOR_TWO:
            return ThreeForTwoOffer(product, argument)
        if offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
            return TenPercentDiscountOffer(product, argument)
        if offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
            return TwoForAmountOffer(product, argument)
        if offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
            return FiveForAmountOffer(product, argument)
        if offer_type == SpecialOfferType.COUPON_DISCOUNT:
            return CouponDiscountOffer(product, argument)
        
        raise ValueError(f"Unknown offer type: {offer_type}")
        
class BundleOffer:
    def __init__(self, bundle_spec, discount_percentage):
        self.bundle_spec = bundle_spec
        self.discount_percentage = discount_percentage

    def can_apply_bundle(self, product_quantities):
        for product, required_qty in self.bundle_spec.items():
            if product not in product_quantities:
                return False
            if product_quantities[product] < required_qty:
                return False
        return True

    def get_discount_amount(self, catalog):
        bundle_price = 0.0
        for product, required_qty in self.bundle_spec.items():
            unit_price = catalog.unit_price(product)
            bundle_price += unit_price * required_qty
        return bundle_price * (self.discount_percentage / 100.0)

    def get_description(self):
        product_names = sorted([p.name for p in self.bundle_spec.keys()])
        names_str = ", ".join(product_names)
        return f"Bundle {self.discount_percentage}% ({names_str})"

    def consume(self, product_quantities):
        for product, required_qty in self.bundle_spec.items():
            product_quantities[product] -= required_qty