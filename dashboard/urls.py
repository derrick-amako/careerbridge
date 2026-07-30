from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/approve-employer/<int:pk>/', views.approve_employer, name='approve_employer'),
    path('admin-panel/deny-employer/<int:pk>/', views.deny_employer, name='deny_employer'),
]
