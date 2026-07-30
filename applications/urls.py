from django.urls import path
from . import views
urlpatterns = [
    path('apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('mine/', views.my_applications, name='my_applications'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/cv/inline/', views.serve_cv_inline, name='serve_cv_inline'),
    path('message/<int:pk>/delete/', views.delete_message, name='delete_message'),
    path('employer/', views.employer_applications, name='employer_applications'),
    path('status/<int:pk>/', views.update_status, name='update_status'),
    path('recommendations/', views.my_recommendations, name='my_recommendations'),
]
