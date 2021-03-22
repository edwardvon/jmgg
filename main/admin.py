from django.contrib import admin
from django.utils.html import format_html
from main.models import Requestments


# Register your models here.
class RequestmentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'area', 'pubdate', 'url_display')

    def url_display(self, obj):
        return format_html(
            f'<a href="{obj.url}" target="_blank">原公告网页</a>'
        )

    list_filter = ('area',)
    date_hierarchy = 'pubdate'


admin.site.register(Requestments, RequestmentsAdmin)
