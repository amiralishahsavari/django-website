"""
URL configuration for DJsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from Recruitment import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.root_redirect, name='root_redirect'),  # ← روت هوشمند
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('update-email/', views.update_email, name='update_email'),
    path('get-form-fields/', views.get_form_fields, name='get-form-fields'),
    path('projects/create/', views.create_project, name='create_project'),
    path('employer/projects/', views.project_list, name='project_list'),#employer_project_list
    path('projects/', views.project_list_view, name='job_project-list'),
    path('projects/<int:project_id>/apply/', views.apply_to_project, name='apply-to-project'),
    path('projects/<int:project_id>/withdraw/', views.withdraw_application, name='withdraw-application'),
    path('my-applications/', views.jobseeker_applications, name='jobseeker-applications'),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/review/', views.review_applicants_view, name='review_applicants'),
    path('applications/<int:app_id>/change-status/<str:status>/', views.change_application_status, name='change_application_status'),

]