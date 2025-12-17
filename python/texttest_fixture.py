"""
Start texttest from a command prompt in the same folder as this file with this command:

texttest -a sr -d .
"""

import sys, csv
import datetime
from pathlib import Path

from model_objects import Product, SpecialOfferType, ProductUnit
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


def read_catalog(catalog_file):
    catalog = FakeCatalog()
    if not catalog_file.exists():
        return catalog
    with open(catalog_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            unit = ProductUnit[row['unit']]
            price = float(row['price'])
            product = Product(name, unit)
            catalog.add_product(product, price)
    return catalog


def read_offers(offers_file, catalog, teller, basket):
    if not offers_file.exists():
        return
        
    with open(offers_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            offer_name_str = row['offer']
            product_names = row['name']
            raw_argument = row['argument']
            
            argument = parse_argument(raw_argument)

            if offer_name_str == "BUNDLE":
                product_list = product_names.split('|')
                bundle_spec = {}
                valid_bundle = True
                for name in product_list:
                    if name in catalog.products:
                        prod = catalog.products[name]
                        bundle_spec[prod] = 1.0
                    else:
                        valid_bundle = False
                
                if valid_bundle:
                    print(f">>> Loading Bundle: {product_names} at {argument}% off")
                    teller.add_bundle_offer(bundle_spec, argument)
            
            elif offer_name_str == "COUPON_DISCOUNT":
                if product_names in catalog.products:
                    product = catalog.products[product_names]
                    print(f">>> Loading Coupon for {product_names}")
                    
                    today = datetime.date.today()
                    code = argument.get('code', 'DEFAULT')
                    valid_days = argument.get('valid_days', 7)
                    
                    offer_arg = {
                        'threshold': argument['threshold'], 
                        'limit': argument['limit'], 
                        'percent': argument['percent']
                    }
                    
                    basket.add_coupon(
                        product=product,
                        code=code,
                        start_date=today,
                        end_date=today + datetime.timedelta(days=valid_days),
                        offer_type=SpecialOfferType.COUPON_DISCOUNT,
                        argument=offer_arg
                    )

            elif offer_name_str in SpecialOfferType.__members__:
                offerType = SpecialOfferType[offer_name_str]
                if product_names in catalog.products:
                    product = catalog.products[product_names]
                    teller.add_special_offer(offerType, product, argument)


def read_basket(cart_file, catalog):
    cart = ShoppingCart()
    if not cart_file.exists():
        return cart
    with open(cart_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            quantity = float(row['quantity'])
            if name in catalog.products:
                product = catalog.products[name]
                cart.add_item_quantity(product, quantity)
    return cart

def parse_argument(arg_str):
    if "=" in arg_str:
        result = {}
        pairs = arg_str.split(';')
        for pair in pairs:
            key, value = pair.split('=')
            try:
                if "." in value:
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except ValueError:
                result[key] = value
        return result
    else:
        return float(arg_str)

def main(args):
    catalog = read_catalog(Path("files/catalog.csv"))
    teller = Teller(catalog)
    basket = read_basket(Path("files/cart.csv"), catalog)
    read_offers(Path("files/offers.csv"), catalog, teller, basket)

    customer_points = 15
    print(f">>> Customer redeeming {customer_points} loyalty points")
    
    receipt = teller.checks_out_articles_from(
        basket, 
        current_date=datetime.date.today(),
        available_points=customer_points
    )

    print("\n" + "="*40)
    print(ReceiptPrinter().print_receipt(receipt))
    print("="*40)

if __name__ == "__main__":
    main(sys.argv[1:])