# Supermarket Receipt Project - Refactoring & Features Summary

## 1. Initial Refactoring
**The Problem:**
The project started with a "God Method" inside `shopping_cart.py`. The `handle_offers()` method contained a massive chain of if/else statements that handled every type of discount calculation. It was hard to read, reused variables (like `x`), that made little sense, and violated the Open/Closed Principle (I would have to modify the file every time I added a new offer type).

**The Solution:**
* **Strategy Pattern:** I moved the math logic out of the Cart and into specific classes inheriting from `Offer` (e.g., ThreeForTwoOffer, TenPercentDiscountOffer).
* **Factory Pattern:** I created an OfferFactory to handle the creation of these objects based on the Enum type.
* **Separation of Query & Modifier:** I changed `handle_offers` to `calculate_discounts`. Instead of modifying the receipt directly as side effect, it now returns a list of discounts.

**Justification:**
This decoupled the `ShoppingCart` from the math. The Cart now just holds data, while the Offer classes are responsible for their own logic.


## 2. Feature: Discounted Bundles
**The Requirement:**
"Buy a Toothbrush and Toothpaste for 10% off."

**The Problems:**
My initial design only supported single-product offers. Also, I had to make sure, that products are not getting discounted twice (e.g. first by bundle, then by ten percent discount).

**The Solution:**
* **BundleOffer Class:** Created a new class to define multi-product rules.
* **DiscountCalculator Service:** I extracted the calculation loop out of `ShoppingCart` into a dedicated service `discount_calculator.py`.
* **Greedy Algorithm:** I implemented a logic that checks for bundles first, applies the best one, and "consumes" the items (removes them from the available list) so they cannot be reused.

**Justification:**
Moving the logic to a Domain Service (`DiscountCalculator`) kept the Cart simple. The consumption logic ensured stable accuracy (preventing double discounts).


## 3. Feature: Coupon-based Discounts
**The Requirement:**
"Buy 6 Orange Juices, get 6 at 50% off. Valid only for specific dates."

**The Problems:**
I needed to introduce Time (validity dates) and ensure coupons were prioritized correctly.

**The Solution:**
* **Generic Coupon Logic:** I renamed the specific requirement to a generic `COUPON_DISCOUNT` type. It accepts a dictionary argument (e.g., `{threshold: 6, limit: 6, percent: 50}`) so it can be reused for any "Buy X Get Y for Z% off" deal.
* **Pipeline Architecture:** I structured `calculate_discounts` into a pipeline:
    1.  **Bundles** (Priority 1 - consumes items)
    2.  **Coupons** (Priority 2 - Checks dates & consumes items)
    3.  **Standard Offers** (Priority 3 - Applied to whatever is left)

**Justification:**
The pipeline approach follows the Single Level of Abstraction Principle (SLAP). The main method is readable, and the consumption logic ensures that coupons and standard offers don't conflict.


## 4. Feature: Loyalty Program
**The Requirement:**
"Earn 1 point per $1 spent. Redeem points as cash discount."

**The Problem:**
The `Teller` class started becoming cluttered with math for point conversion and redemption logic.

**The Solution:**
* **LoyaltyService:** I extracted all loyalty logic (point earning and redemption) into `loyalty_service.py`.
* **Orchestration:** The `Teller` class now simply delegates work: it asks `DiscountCalculator` for discounts and `LoyaltyService` for points.

**Justification:**
This maintains the Single Responsibility Principle. The `Teller` is just an orchestrator, while the Service handles the business rules.