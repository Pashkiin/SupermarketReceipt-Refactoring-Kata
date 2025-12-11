from enum import Enum
import math
from abc import ABC, abstractmethod


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

class Discount:
    def __init__(self, product, description, discount_amount):
        self.product = product
        self.description = description
        self.discount_amount = discount_amount

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
        
        raise ValueError(f"Unknown offer type: {offer_type}")