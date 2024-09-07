from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Product)

class AlbumItemAdmin(admin.ModelAdmin):
     raw_id_fields = ['product']
admin.site.register(models.AlbumItem, AlbumItemAdmin)

class InventoryAdmin(admin.ModelAdmin):
     raw_id_fields = ['product']
admin.site.register(models.Inventory, InventoryAdmin)
