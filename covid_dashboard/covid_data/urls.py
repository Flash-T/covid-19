from django.urls import path
from . import views

app_name = 'covid_data'

urlpatterns = [
    # 页面URL
    path('', views.index, name='index'),
    
    # API URL
    path('api/china-map/', views.china_map_data, name='china_map_data'),
    path('api/trend-chart/', views.trend_chart_data, name='trend_chart_data'),
    path('api/province-rank/', views.province_rank_data, name='province_rank_data'),
    path('api/province/<str:province_name>/', views.province_detail, name='province_detail'),
    path('api/provinces/', views.province_list, name='province_list'),
    path('api/dates/', views.available_dates, name='available_dates'),
]