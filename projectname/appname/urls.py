from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Public pages
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # 🔹 Authentication
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('staff/signup/', views.staff_signup, name='staff_signup'),

    # 🔹 Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('studentdashboard/', views.studentdashboard, name='studentdashboard'),
    path('staffdashboard/', views.staffdashboard, name='staffdashboard'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),

    # 🔹 Profile Updates
    path('update_student/', views.update_student, name='update_student'),
    path('staff/update/', views.update_staff, name='update_staff'),
    path('update-profile/', views.update_admin_profile, name='update_admin_profile'),
    path('staff/update/<int:user_id>/', views.update_staff, name='update_staff'),  # Admin updating a staff

    # 🔹 Staff Course Upload and Manage
    path('staff/upload-course/', views.upload_course, name='upload_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # 🔹 Admin Course Management
    path('admindashboard/approve-course/<int:course_id>/', views.approve_course, name='approve_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),

    # 🔹 Enrollment
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),

    # 🔹 View All Courses
    path('all-courses/', views.all_courses, name='all_courses'),

    # 🔹 Admin Delete Users
    path('delete/student/<int:user_id>/', views.delete_student, name='delete_student'),
    path('delete/staff/<int:user_id>/', views.delete_staff, name='delete_staff'),

    # Optional (if you want a separate page for course approvals)
    path('course-approval/', views.course_approval, name='course_approval'),
]
