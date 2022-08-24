from django.contrib import admin
from .models import Product
# Register your models here.


admin.site.site_header="Shop And Sell Website"
admin.site.site_title = "ABC Buying"
admin.site.index_title = "Manage the ABC Buying Website"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','desc')
#searching based on name
    search_fields = ('name',)
#searching based on desc
    # search_fields = ('desc',)


#Custom Actions
    def set_price_to_zero(self,request,queryset):
        queryset.update(price=0)

    actions = ('set_price_to_zero',)

#admin fields direct editing
    list_editable = ('price','desc')

admin.site.register(Product,ProductAdmin)