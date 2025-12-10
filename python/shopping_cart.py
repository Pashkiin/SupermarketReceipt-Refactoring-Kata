import math
from model_objects import ProductQuantity, SpecialOfferType, Discount

class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt, offers, catalog):
        for p, quantity in self._product_quantities.items():
            if p in offers:
                offer = offers[p]
                unit_price = catalog.unit_price(p)
                discount = None

                if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                    discount = self._handle_three_for_two(p, quantity, unit_price)
                
                elif offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                    discount = self._handle_ten_percent_discount(p, quantity, unit_price, offer)
                
                elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                    discount = self._handle_two_for_amount(p, quantity, unit_price, offer)
                
                elif offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                    discount = self._handle_five_for_amount(p, quantity, unit_price, offer)

                if discount:
                    receipt.add_discount(discount)

    def _handle_three_for_two(self, product, quantity, unit_price):
        quantity_as_int = int(quantity)
        if quantity_as_int <= 2:
            return None
            
        discount_amount = quantity * unit_price - (
            (math.floor(quantity_as_int / 3) * 2 * unit_price) + quantity_as_int % 3 * unit_price)
        return Discount(product, "3 for 2", -discount_amount)

    def _handle_ten_percent_discount(self, product, quantity, unit_price, offer):
        discount_amount = quantity * unit_price * offer.argument / 100.0
        return Discount(product, str(offer.argument) + "% off", -discount_amount)

    def _handle_two_for_amount(self, product, quantity, unit_price, offer):
        quantity_as_int = int(quantity)
        if quantity_as_int < 2:
            return None

        total = offer.argument * math.floor(quantity_as_int / 2) + quantity_as_int % 2 * unit_price
        discount_n = unit_price * quantity - total
        return Discount(product, "2 for " + str(offer.argument), -discount_n)

    def _handle_five_for_amount(self, product, quantity, unit_price, offer):
        quantity_as_int = int(quantity)
        if quantity_as_int < 5:
            return None
        
        discount_total = unit_price * quantity - (
            offer.argument * math.floor(quantity_as_int / 5) + quantity_as_int % 5 * unit_price)
        return Discount(product, "5 for " + str(offer.argument), -discount_total)