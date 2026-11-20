from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order/new/', views.order_create, name='order_create'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/edit/', views.order_update, name='order_update'),
    path('order/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('order/<int:pk>/stage-update/', views.quick_stage_update, name='quick_stage_update'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('manifest.json', views.manifest_view, name='manifest'),
]
