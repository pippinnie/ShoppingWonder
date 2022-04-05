from django.contrib import admin
from django.apps import apps

from .models import Product, Image

# Register your models here.
LIST_DISPLAY = {
    
}


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = LIST_DISPLAY.get(
            model, [field.name for field in model._meta.fields]
        )
        super(ListAdminMixin, self).__init__(model, admin_site)

class ImageInline(admin.TabularInline):
    model = Image


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline
    ]
    list_display = ("id", "title", "parent", "active", "minQty", "sold", "views")

admin.site.register(Product, ProductAdmin)

models = apps.get_models()

for model in models:
    admin_class = type("AdminClass", (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
