from django.contrib import admin
from .models import Province, City, DailyStatistics

class CityInline(admin.TabularInline):
    model = City
    extra = 0
    fields = ['name', 'confirmed_count', 'suspected_count', 'cured_count', 'dead_count']
    can_delete = False

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'data_date', 'confirmed_count', 'suspected_count', 'cured_count', 'dead_count')
    list_filter = ('data_date', 'short_name')
    search_fields = ('name', 'short_name')
    date_hierarchy = 'data_date'
    inlines = [CityInline]
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-data_date', 'name')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'data_date', 'confirmed_count', 'suspected_count', 'cured_count', 'dead_count')
    list_filter = ('data_date', 'province__short_name')
    search_fields = ('name', 'province__name')
    date_hierarchy = 'data_date'
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-data_date', 'province__name', 'name')

@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'confirmed_count', 'suspected_count', 'cured_count', 'dead_count', 
                   'confirmed_incr', 'suspected_incr', 'cured_incr', 'dead_incr')
    list_filter = ('date',)
    date_hierarchy = 'date'
    list_per_page = 30
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-date')
    
    def has_add_permission(self, request):
        return False  # 禁止手动添加，只能通过导入数据创建

# 自定义管理界面标题和头部
admin.site.site_header = 'COVID-19疫情数据管理'
admin.site.site_title = 'COVID-19管理后台'
admin.site.index_title = '数据管理' 