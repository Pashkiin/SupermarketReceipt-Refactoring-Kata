import unittest
import datetime

from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


class SupermarketTest(unittest.TestCase):
    def setUp(self):
        self.catalog = FakeCatalog()
        self.teller = Teller(self.catalog)
        self.cart = ShoppingCart()

        self.toothbrush = Product("toothbrush", ProductUnit.EACH)
        self.catalog.add_product(self.toothbrush, 0.99)
        
        self.apples = Product("apples", ProductUnit.KILO)
        self.catalog.add_product(self.apples, 1.99)

    def test_no_discounts(self):
        self.cart.add_item_quantity(self.apples, 2.0)
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        # 2kg * 1.99 = 3.98
        self.assertAlmostEqual(receipt.total_price(), 3.98, places=2)
        self.assertEqual([], receipt.discounts)

    def test_ten_percent_discount(self):
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.toothbrush, 10.0)

        self.cart.add_item_quantity(self.toothbrush, 1.0)
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        # 0.99 - 0.099 = 0.891
        self.assertAlmostEqual(receipt.total_price(), 0.891, places=3)
        self.assertEqual(1, len(receipt.discounts))

    def test_three_for_two_discount(self):
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.toothbrush, 0.0)
        
        self.cart.add_item_quantity(self.toothbrush, 3.0)   
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        # 2 * 0.99 = 1.98
        self.assertAlmostEqual(receipt.total_price(), 1.98, places=2)
        self.assertEqual(1, len(receipt.discounts))

    def test_three_for_two_discount_with_excess_items(self):
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.toothbrush, 0.0)
        
        self.cart.add_item_quantity(self.toothbrush, 4.0) 
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        # (2 * 0.99) + (1 * 0.99) = 2.97
        self.assertAlmostEqual(receipt.total_price(), 2.97, places=2)

    def test_two_for_amount_discount(self):
        self.teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, self.toothbrush, 1.50)
        self.cart.add_item_quantity(self.toothbrush, 2.0)
        
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        self.assertAlmostEqual(receipt.total_price(), 1.50, places=2)
        self.assertEqual(1, len(receipt.discounts))

    def test_five_for_amount_discount(self):
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.toothbrush, 4.00)   
        self.cart.add_item_quantity(self.toothbrush, 5.0)
        
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        self.assertAlmostEqual(receipt.total_price(), 4.00, places=2)
        self.assertEqual(1, len(receipt.discounts))

    def test_five_for_amount_discount_with_six_items(self):
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.toothbrush, 4.00)
        self.cart.add_item_quantity(self.toothbrush, 6.0)
        
        receipt = self.teller.checks_out_articles_from(self.cart)
        
        self.assertAlmostEqual(receipt.total_price(), 4.99, places=2)

    def test_bundle_discount(self):
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        chocolate = Product("chocolate", ProductUnit.EACH)
        self.catalog.add_product(toothpaste, 1.79)
        self.catalog.add_product(chocolate, 5.00)
        
        self.teller.add_bundle_offer(
            bundle_products={self.toothbrush: 1.0, toothpaste: 1.0}, 
            discount_percentage=10.0
        )

        self.teller.add_bundle_offer(
            bundle_products={chocolate: 1.0, toothpaste: 1.0}, 
            discount_percentage=10.0
        )
        
        self.cart.add_item_quantity(self.toothbrush, 1.0)
        self.cart.add_item_quantity(toothpaste, 1.0)
        self.cart.add_item_quantity(chocolate, 1.0)
        
        receipt = self.teller.checks_out_articles_from(self.cart)


        # Should apply only one bundle discount (the best one)
        # (5.00 + 1.79) * 10% = 0.679
        # 7.78 - 0.679 = 7.101
        self.assertAlmostEqual(receipt.total_price(), 7.101, places=3)
        self.assertEqual(1, len(receipt.discounts))

    def test_coupon_valid_date(self):
        juice = Product("orange juice", ProductUnit.EACH)
        self.catalog.add_product(juice, 2.00)
        
        today = datetime.date(2025, 1, 1)
        self.cart.add_item_quantity(juice, 12.0)
        coupon_arg = {'threshold': 6, 'limit': 6, 'percent': 50.0}

        self.cart.add_coupon(
            product=juice, 
            code="OJ-DEAL", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 10),
            offer_type=SpecialOfferType.COUPON_DISCOUNT,
            argument=coupon_arg
        )
        
        receipt = self.teller.checks_out_articles_from(self.cart, current_date=today)
        
        # Coupon applied: 6 * 2.00 + (6 * 2.00)*50% = 18.00
        self.assertAlmostEqual(receipt.total_price(), 18.00, places=2)
        self.assertEqual(1, len(receipt.discounts))

    def test_coupon_invalid_date(self):
        juice = Product("orange juice", ProductUnit.EACH)
        self.catalog.add_product(juice, 2.00)
        
        today = datetime.date(2025, 2, 1)
        self.cart.add_item_quantity(juice, 12.0)
        coupon_arg = {'threshold': 6, 'limit': 6, 'percent': 50.0}
        
        self.cart.add_coupon(
            product=juice, 
            code="OJ-DEAL", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 10),
            offer_type=SpecialOfferType.COUPON_DISCOUNT,
            argument=coupon_arg
        )
        
        receipt = self.teller.checks_out_articles_from(self.cart, current_date=today)
        
        # Coupon ignored: 12 * 2.00 = 24.00
        self.assertAlmostEqual(receipt.total_price(), 24.00, places=2)
        self.assertEqual(0, len(receipt.discounts))

    def test_coupon_used_only_once(self):       
        juice = Product("orange juice", ProductUnit.EACH)
        self.catalog.add_product(juice, 2.00)

        today = datetime.date(2025, 1, 1)
        self.cart.add_item_quantity(juice, 24.0)
        coupon_arg = {'threshold': 6, 'limit': 6, 'percent': 50.0}
        
        self.cart.add_coupon(
            product=juice, 
            code="OJ-ONCE", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 10),
            offer_type=SpecialOfferType.COUPON_DISCOUNT,
            argument=coupon_arg
        )
        
        self.cart.add_coupon(
            product=juice, 
            code="OJ-ONCE", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 10),
            offer_type=SpecialOfferType.COUPON_DISCOUNT,
            argument=coupon_arg
        )
        
        receipt = self.teller.checks_out_articles_from(self.cart, current_date=today)
        
        # One coupon applied: 18 * 2.00 + (6 * 2.00)*50% = 42.00
        self.assertAlmostEqual(receipt.total_price(), 42.00, places=2)
        self.assertEqual(1, len(receipt.discounts))

    def test_coupon_consumes_items_double_offer(self):
        juice = Product("orange juice", ProductUnit.EACH)
        self.catalog.add_product(juice, 2.00)
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, juice, 0.0)

        today = datetime.date(2025, 1, 1)
        self.cart.add_item_quantity(juice, 13.0)
        coupon_arg = {'threshold': 5, 'limit': 5, 'percent': 50.0}
        
        self.cart.add_coupon(
            product=juice, 
            code="OJ-DEAL", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 10),
            offer_type=SpecialOfferType.COUPON_DISCOUNT,
            argument=coupon_arg
        )
        
        receipt = self.teller.checks_out_articles_from(self.cart, current_date=today)
        # (5 * 2.00) + (5 * 1.00) + (3 for 2 -> 2*2) = 19.00
        self.assertAlmostEqual(receipt.total_price(), 19.00, places=2)
        self.assertEqual(2, len(receipt.discounts))