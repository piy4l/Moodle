from django.conf.urls import url
from basic_app import views
from django.urls import path

#TEMPLATE URLS!
app_name = 'basic_app'

urlpatterns = [
    url(r'^user_login/$', views.user_login, name = 'user_login'),
    #url(r'^course_details/(?P<session_name>\w+)/(?P<course_id>\w+)/$', views.course_details, name='course_details'),
    #url(r'^upload_file/$', views.upload_file, name = 'upload_file'),
    url(r'^user_logout/$', views.user_logout, name = 'user_logout'),
    url(r'^home/$', views.homepage, name = 'homepage'),
    url(r'^home/my_courses/$', views.my_courses, name = 'my_courses'),
    url(r'^moodle_admin/$', views.moodle_admin, name = 'moodle_admin'),
    url(r'^moodle_admin/user_desc_choice/$', views.user_desc_choice, name = 'user_desc_choice'),
    url(r'^moodle_admin/user_desc_choice/view/$', views.user_desc_view, name = 'user_desc_view'),
    url(r'^moodle_admin/user_desc_choice/add/$', views.user_desc_add, name = 'user_desc_add'),
    url(r'^moodle_admin/user_desc_choice/update/$', views.user_desc_update, name = 'user_desc_update'),
    url(r'^moodle_admin/user_desc_choice/delete/$', views.user_desc_delete, name = 'user_desc_delete'),
    url(r'^moodle_admin/course_choice/$', views.course_choice, name = 'course_choice'),
    url(r'^moodle_admin/course_choice/view/$', views.course_view, name = 'course_view'),
    url(r'^moodle_admin/course_choice/add/$', views.courses_add, name = 'courses_add'),
    url(r'^moodle_admin/course_choice/update/$', views.courses_update, name = 'courses_update'),
    url(r'^moodle_admin/course_choice/delete/$', views.courses_delete, name = 'courses_delete'),
    url(r'^moodle_admin/student_choice/$', views.student_choice, name = 'student_choice'),
    url(r'^moodle_admin/student_choice/view/$', views.student_view, name = 'student_view'),
    url(r'^moodle_admin/student_choice/add/$', views.students_add, name = 'students_add'),
    url(r'^moodle_admin/student_choice/update/$', views.students_update, name = 'students_update'),
    url(r'^moodle_admin/student_choice/delete/$', views.students_delete, name = 'students_delete'),
    url(r'^moodle_admin/teacher_choice/$', views.teacher_choice, name = 'teacher_choice'),
    url(r'^moodle_admin/teacher_choice/view/$', views.teacher_view, name = 'teacher_view'),
    url(r'^moodle_admin/teacher_choice/add/$', views.teachers_add, name = 'teachers_add'),
    url(r'^moodle_admin/teacher_choice/update/$', views.teachers_update, name = 'teachers_update'),
    url(r'^moodle_admin/teacher_choice/delete/$', views.teachers_delete, name = 'teachers_delete'),
    url(r'^moodle_admin/student_course_relation_choice/$', views.student_course_relation_choice, name = 'student_course_relation_choice'),
    url(r'^moodle_admin/student_course_relation_choice/view/$', views.student_course_relation_view, name = 'student_course_relation_view'),
    url(r'^moodle_admin/student_course_relation_choice/add/$', views.student_course_relation_add, name = 'student_course_relation_add'),
    url(r'^moodle_admin/student_course_relation_choice/delete/$', views.student_course_relation_delete, name = 'student_course_relation_delete'),
    url(r'^moodle_admin/teacher_course_relation_choice/$', views.teacher_course_relation_choice, name = 'teacher_course_relation_choice'),
    url(r'^moodle_admin/teacher_course_relation_choice/view/$', views.teacher_course_relation_view, name = 'teacher_course_relation_view'),
    url(r'^moodle_admin/teacher_course_relation_choice/add/$', views.teacher_course_relation_add, name = 'teacher_course_relation_add'),
    url(r'^moodle_admin/teacher_course_relation_choice/delete/$', views.teacher_course_relation_delete, name = 'teacher_course_relation_delete'),
]
