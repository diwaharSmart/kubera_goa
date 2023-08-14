"""kubera_goa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from KuberaApp import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
     path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
     path('accept_order/<int:draw_id>/', views.accept_orders_and_calculate_loot, name='accept_order'),
     path('calculate_order/<int:draw_id>/', views.calculate_orders_and_calculate_loot, name='calculate_order'),
     path('generate_preview_result/<int:draw_id>/', views.generate_preview_result, name='generate_preview_result'),
     path('generate_result/<int:draw_id>/<str:number>', views.generate_result, name='generate_result'),
     path('', views.home, name='home'),
     path('draws/', views.draws_list, name='draws_list'),
     path('view-tickets/', views.view_tickets, name='view_tickets'),
     path('view-orders/', views.view_orders, name='view_orders'),
     path('search-agent/', views.search_agent, name='search_agent'),
     path('agent-search-success/<str:agent_id>/', views.agent_search_success, name='agent_search_success'),
    #  path('agent-search-failure/', views.agent_search_failure, name='agent_search_failure'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('agent/list/', views.agent_list, name='agent_list'),
    path('agent/settlement/<str:username>/', views.agent_settlement, name='agent_settlement'),
    path('agent/settlements/<str:username>/', views.settle_winnings, name='settle_winning'),
    path('create_order/<str:draw_id>/', views.create_order, name='create_order'),
    path('create_formset/', views.create_formset, name='create_formset'),
    path('wallet/', views.wallet, name='wallet'),
    path('order_preview/<int:order_id>/', views.order_preview, name='order_preview'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('edit_bank_info/', views.edit_bank_info, name='edit_bank_info'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),
    path('customer_settlements/', views.customer_settlements, name='customer_settlements'),
    path('settle_order/<int:order_id>/', views.settle_order, name='settle_order'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
