"""learning_user URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url, include
from django.conf import settings
from basic_app import views
from django.urls import path
from django.views.static import serve


urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^admin/', admin.site.urls),
    url(r'^basic_app/', include('basic_app.urls')),
    url(r'^logout/$', views.user_logout, name = 'logout'),
    path('course_details/<str:session_name>/<str:course_id>/week_choice/', views.course_details, name = 'course_details'),
    path('course_details/<str:session_name>/<str:course_id>/week/<int:week_number>/view/', views.course_week_details, name = 'course_week_details'),
    path('course_details/<str:session_name>/<str:course_id>/week_number/<int:week_number>/upload_files/', views.upload_file, name = 'upload_files'),
    path('course_details/<str:session_name>/<str:course_id>/create_post/', views.create_post, name = 'create_post'),
    path('course_details/<str:session_name>/<str:course_id>/show_post/', views.show_post, name = 'show_post'),
    path('course_details/<str:post_id>/comments/', views.comments, name = 'comments'),
    path('course_details/<str:session_name>/<str:course_id>/week_number/<int:week_number>/post_other_links/', views.post_other_links, name = 'post_other_links'),
    path('course_details/<str:session_name>/<str:course_id>/week_number/<int:week_number>/create_submission_link/', views.create_submission_link, name = 'create_submission_link'),
    path('course_details/<str:session_name>/<str:course_id>/week_number/<int:week_number>/view_submission_link/<str:link_title>', views.view_submission_link, name = 'view_submission_link'),
    #url(r'^download/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
