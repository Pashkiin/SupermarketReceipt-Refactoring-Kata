from model_objects import Discount, LOYALTY_POINT_VALUE

class LoyaltyService:
    def apply_reduction(self, receipt, available_points):
        if available_points <= 0:
            return

        current_total = receipt.total_price()
        max_redemption_value = available_points * LOYALTY_POINT_VALUE

        actual_redemption_value = min(current_total, max_redemption_value)
        
        if actual_redemption_value > 0:
            receipt.add_discount(Discount(
                product=None, 
                description="Loyalty Discount", 
                discount_amount=-actual_redemption_value
            ))

    def calculate_points_earned(self, receipt):
        final_total = receipt.total_price()
        points_earned = int(final_total)
        receipt.add_loyalty_points(points_earned)