from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.Login, name='login'),
    path("get-all-students/", views.get_all_students, name='get_all_students'),
    path('get-student-by/<str:Sid>/', views.get_student, name='get_student'),
    path("register/", views.Register, name='register'),
    path("update-student/<int:pk>/", views.update_student, name="update_student"),
    path("remove-student/<str:Sid>/", views.remove_student, name='remove_student'),
    path('enrollment/<str:Sid>/', views.get_enrollment_details, name='enrolements-deatiles'),
    path('updatemarks/<str:id>/', views.update_marks, name='update-marks'),
    path('average-age/', views.average_age, name='average_age'),
    path('courses/', views.get_all_courses, name='get_all_courses'),
    path('enrollments/by-course/<str:course_name>/', views.get_enrolled_details, name='get_enrolled_details'),
    path('courses/summary/', views.course_statistics, name='course_summary'),
    path('courses/add/', views.add_course, name='add-course'),
    path('courses/update/<str:courseId>/', views.update_course, name='course-update'),
    path('courses/delete/<str:courseId>/', views.delete_course, name='course-delete'),
    path('get_students/', views.get_students),
    path('get_courses/', views.get_courses),
    path('get_enrollments/', views.get_enrollments, name='all_enrolled_students'),
    path('add_enrollment/', views.add_enrollment, name='ads_enrolement'),
    path('update_enrollment/<str:enrollment_id>/', views.update_enrollment, name='update-enrolement'),
    path('delete_enrollment/<str:enrollment_id>/', views.delete_enrollment, name='delete_enrollment'),
    path('all_students_marks/', views.all_students_marks, name='all_students_marks'),
    path('update_marks_records/<str:enrollment_id>/', views.update_marks_record, name='update-marks'),


    path("ren", views.ren, name='ren'),
]