from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.Login, name='login'),
    path("get-all-students/", views.get_all_students, name='get_all_students'),
    path('get-student-by/<str:Sid>/', views.get_student, name='get_student'),
    path("register/", views.Register, name='register'),
    path("update-student/<int:pk>/", views.update_student, name="update_student"),
    path("remove-student/<str:Sid>/", views.remove_student, name='remove_student'),


    path("ren", views.ren, name='ren'),
]