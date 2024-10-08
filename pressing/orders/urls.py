from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Add this import
from .views import apply_portfolio, payment_page, download_receipt  # Import process_payment
from .views import chat_view, marketing_promotions, add_pressing
from .views import analytics_view, view_portfolio
from .views import track_deliveries, view_deliveries, schedule_pickup, view_invoices, track_vehicle
from .views import chat_room, send_message


urlpatterns = [
    path('', views.home, name='home'), # Root URL routed to the home view
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('logout/', views.logout, name='logout'),
    path('panel/admin/', views.admin_panel, name='admin_panel'),
    path('panel/pressing-manager/', views.pressing_manager, name='pressing_manager'),
    path('panel/clients/', views.clients_panel, name='clients_panel'),
    path('panel/deliver/', views.deliver_panel, name='deliver_panel'),
    path("panel/pressing_search/", views.pressing_fetch_by_location, name="pressing_search"),
    path("panel/pressing_booking/", views.pressing_view, name="pressing_booking"),
    path("panel/pressing_comment/", views.pressing_comment, name="pressing_comment"),
    path("panel/pressing_appointment/<int:id>/", views.pressing_appointment, name="pressing_appointment"),

    path('about_us/', views.about_us, name='about_us'),
    path('setting/', views.setting, name='setting'),
    path('customer_feedback/', views.customer_feedback, name='customer_feedback'),
    path('apply-portfolio/', views.apply_portfolio, name='apply_portfolio'),
    path('predefined_portfolios/', views.predefined_portfolios, name='predefined_portfolios'),
    path('selected_portfolio/<int:id>/', views.selected_portfolio, name='selected_portfolio'),
    path('panel/edit_pressing/<int:id>/<str:response>/', views.edit_pressing_status, name="edit_pressing_profile"),
    path('panel/edit_pressing_status/', views.get_pressings, name="edit_pressing_status"),
    path('load-towns/', views.load_towns, name='load_towns'),
    path('load-quarters/', views.load_quarters, name='load_quarters'),

    path('payment_page/', payment_page, name='payment_page'),
    path("render-map/<int:id>/", views.render_pressing_map, name="render_map_details"),
    path('view_payments/', views.payment_status_view, name='view_payments'),
    path('download-receipt/<int:receipt_id>/', download_receipt, name='download_receipt'),
    path('chat/', chat_view, name='chat'),
    path('user-management/', views.user_management, name='user_management'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('about_us_dev/', views.about_us_dev, name='about_us_dev'),
    path('marketing-promotions/', marketing_promotions, name='marketing_promotions'),
    path('platform_management/add_pressing/', add_pressing, name='add_pressing'),

    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('chat/send_message/', views.send_message, name='send_message'),
    path('chat/get_messages/<str:room_name>/', views.get_messages, name='get_messages'),
    
    path('analytics/', analytics_view, name='analytics'),
    path('portfolio/<int:user_id>/', view_portfolio, name='view_portfolio'),
    path('track_deliveries/', track_deliveries, name='track_deliveries'),
    path('view_deliveries/', view_deliveries, name='view_deliveries'),
    path('schedule_pickup/', schedule_pickup, name='schedule_pickup'),
    path('view_invoices/', view_invoices, name='view_invoices'),
    path('track_vehicle/', track_vehicle, name='track_vehicle'),
    path('chat/<str:room_name>/', chat_room, name='chat_room'),
    path('send_message/<str:room_name>/', send_message, name='send_message'),
    path('pending/', views.pending, name='pending'),
    path('setting_user/', views.setting_user, name='setting_user'),
    path('profile_user/', views.profile_user, name='profile_user'),



#deliver url
    path('setting_deliver/', views.setting_deliver, name='setting_deliver'),
    path('manage-deliver/', views.manage_deliver_view, name='manage_deliver'),
    path('benefits/', views.benefits_view, name='benefits'),
    path('account-history/', views.account_history, name='account_history'),
    path('pressings/', views.pressing_list, name='pressing_list'),
    path('pressings/add/', views.pressing_add, name='pressing_add'),
    path('pressings/edit/<int:pk>/', views.pressing_edit, name='pressing_edit'),
    path('pressings/delete/<int:pk>/', views.pressing_delete, name='pressing_delete'),
    path('manage-publicity/', views.manage_publicity, name='manage_publicity'),
    path('rate-deliveries/', views.rate_deliveries, name='rate_deliveries'),


    path('deliver-statistics/', views.deliver_statistics, name='deliver_statistics'),
    path('give-bonus/<int:user_id>/', views.give_bonus, name='give_bonus'),

]