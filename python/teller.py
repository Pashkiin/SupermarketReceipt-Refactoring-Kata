from model_objects import OfferFactory
from receipt import Receipt


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.offer_factory = OfferFactory()

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = self.offer_factory.create(offer_type, product, argument)

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        product_quantities = the_cart.items
        for pq in product_quantities:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        discounts = the_cart.calculate_discounts(self.offers, self.catalog)
        for discount in discounts:
            receipt.add_discount(discount)

        return receipt
