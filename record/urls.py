from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.record_list, name='record_list'),
    path('grouped/', views.grouped_records, name='grouped_records'),
    path('add/', views.add_record, name='add_record'),
    path('edit/<int:record_id>/', views.edit_record, name='edit_record'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'), 
    path('profile/', views.profile_view, name='profile'),
    path('predict-disease/', views.predict_disease_view, name='predict_disease'),
    path('about/', views.about_view, name='about'),

] 