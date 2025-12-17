from model_objects import ProductQuantity, Coupon

class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}
        self._coupons = []

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

    @property
    def coupons(self):
        return self._coupons

    def add_coupon(self, product, code, start_date, end_date, offer_type, argument):
        for c in self._coupons:
            if c.code == code:
                return
        self._coupons.append(Coupon(product, code, start_date, end_date, offer_type, argument))