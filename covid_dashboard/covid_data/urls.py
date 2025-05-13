from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'covid_data'

urlpatterns = [
    # 页面URL
    path('', views.home_redirect_view, name='home'),
    path('dashboard/', login_required(views.index), name='index'),
    path('province/<str:province_name>/', login_required(views.province_detail_page), name='province_detail_page'),
    
    # 用户认证URL
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # API URL
    path('api/china-map/', views.china_map_data, name='china_map_data'),
    path('api/trend-chart/', views.trend_chart_data, name='trend_chart_data'),
    path('api/province-rank/', views.province_rank_data, name='province_rank_data'),
    path('api/province/<str:province_name>/', views.province_detail, name='province_detail'),
    path('api/provinces/', views.province_list, name='province_list'),
    path('api/dates/', views.available_dates, name='available_dates'),
    path('api/status-pie/', views.status_pie_data, name='status_pie_data'),
]