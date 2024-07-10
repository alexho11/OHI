from django.urls import path,re_path
from . import views

app_name = 'ohi'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('params', views.params, name='params'),
    path('health',views.health, name='health'),
    path('download', views.download, name='download'),
    path('overview', views.overview, name='overview'),
    path('delete_record', views.delete_record, name='delete_record'),
    path('progress', views.progress, name='progress'),
    path('param_visual', views.param_visual, name='param_visual'),
    path('hotspots', views.hotspots, name='hotspots'),
    path('delete_health_record', views.delete_health_record, name='delete_health_record'),
    path('health_visual', views.health_visual, name='health_visual'),
]