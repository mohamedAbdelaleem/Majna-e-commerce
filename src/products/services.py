from typing import List, Dict
from django.core.exceptions import ValidationError
from django.conf import settings
from brands.services import BrandSelector
from utils.storage import SupabaseStorageService
from common.validators import validate_file_format, validate_file_size
from stores import models

MAX_ALBUM_ITEMS = 10

class ProductService:
    def __init__(self) -> None:
        self.supabase = SupabaseStorageService()
        self.brand_selector = BrandSelector()

    def create(self, **product_data):
        pass

    def add_album_items(product_id, album_items_data: List[Dict]):
        pass

    def _validate_album_items(album_items_data: List[Dict]):
        if len(album_items_data) > MAX_ALBUM_ITEMS:
            raise ValidationError("Album Items can not be more than 10")
        
        num_of_covers = 0
        for item in album_items_data:
            image, is_cover = item["image"], item["is_cover"]
            validate_file_size(image, settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
            validate_file_format(image, ['jpg', 'png', 'jpeg'])
            if is_cover:
                num_of_covers += 1
        
        if num_of_covers != 1:
            raise ValidationError("Album must have One cover image")


    def _validate_inventory(inventory: List[Dict], distributor_pk):
        stores = [inv["store_pk"] for inv in inventory]
        stores_num = (
            models.Store.objects.filter(pk__in=stores, distributor_id=distributor_pk)
            .values("distributor_id")
            .count()
        )

        if stores_num != len(stores):
            raise ValidationError("Invalid stores provided")
