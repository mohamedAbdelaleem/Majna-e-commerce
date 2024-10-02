from typing import Dict, List, Union
from rest_framework.exceptions import PermissionDenied
from common.api.exceptions import Conflict
from orders.models import Order
from reviews.models import Review


class ReviewService:
    def __init__(self) -> None:
        self.selector = ReviewSelector()

    def create(self, product_pk: int, customer_pk, **review_data):
        self.selector.validate_review_ability(customer_pk, product_pk)
        order_date = self.selector.find_latest_delivered_order(
            customer_pk, product_pk
        ).ordered_at

        review = Review(
            product_id=product_pk,
            customer_id=customer_pk,
            order_date=order_date,
            **review_data,
        )
        review.full_clean()
        review.save()

    def update(self, review: Review, **data: Dict):
        for key, val in data.items():
            setattr(review, key, val)
        review.full_clean()
        review.save()
    
    def delete(self, review: Review):
        review.delete()


class ReviewSelector:
    def review_list(self, ordering: Union[List[str], None] = None, **filters):
        reviews = Review.objects.filter(**filters)
        if ordering:
            reviews = reviews.order_by(*ordering)
        return reviews

    def validate_review_ability(self, customer_pk: int, product_pk: int):
        order = self.find_latest_delivered_order(customer_pk, product_pk)
        if not order:
            raise PermissionDenied("Customer can't review this product")
        review_exists = Review.objects.filter(
            customer_id=customer_pk, product_id=product_pk
        ).exists()
        if review_exists:
            raise Conflict("A review exists for this product")

    def find_latest_delivered_order(self, customer_pk: int, product_pk: int):
        order = (
            Order.objects.filter(
                customer_id=customer_pk,
                status="delivered",
                orderitem__product_id=product_pk,
            )
            .order_by("-ordered_at")
            .first()
        )

        return order
