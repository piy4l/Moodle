from django.shortcuts import render
from basic_app.forms import UserForm, UserProfileInfoForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Course
from django.db import connection
import cx_Oracle
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256
from django.core.files.storage import FileSystemStorage
import os
from pathlib import Path
curr_user = ""
logged_in = False
dsn_tns  = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
conn = cx_Oracle.connect(user='ruhan',password='123',dsn=dsn_tns)
is_teacher = 0
# Create your views here.

def index(request):
    return render(request, 'basic_app/index.html', {'logged_in' : logged_in})

def view_submission_link(request, session_name, course_id, week_number, link_title):
    file_uploaded = False
    c = conn.cursor()
    c.execute("""SELECT  DESCRIPTION, DUE_DATE, DUE_DATE - SYSDATE FROM SUBMISSION_LINK WHERE COURSE_ID = :a AND SESSION_NAME = :b AND WEEK_NO = :c AND LINK_TITLE = :d""",
              {"a" : course_id,
               "b" : session_name,
               "c" : week_number,
               "d" : link_title})
    result = c.fetchall()
    c.close()

    submission_details = []

    for r in result:
       description = r[0]
       due_date = r[1]
       time_remaining = r[2]
       total_hours = time_remaining * 24
       days = int(time_remaining)
       remaining_hours = total_hours - days * 24
       hours = int(remaining_hours)
       remaining_minutes = remaining_hours * 60 - hours * 60
       minutes = int(remaining_minutes)
       row = {'description':description, 'due_date':due_date, 'time_remaining':time_remaining}
       submission_details.append(row)

       if request.method == 'POST':
           user_id = curr_user
           week = 'week ' + str(week_number)
           session = str(session_name)
           user_folder = 'static/basic_app/files/' + session
           course = str(course_id)
           user_folder = user_folder + '/' + course + '/' + week + '/' + link_title
           #user_folder = os.path.join(user_folder, session_name, course_id, week)
           print(user_folder)
           Path(user_folder).mkdir(parents=True, exist_ok=True)
           myfile = request.FILES['filename']
           filename = myfile.name
           print(filename)
           fs = FileSystemStorage(location=user_folder)

           filename = fs.save(filename, myfile)
           print(filename)
           #file_url = fs.url(filename)
           #print(file_url)
           file_path = os.path.join(user_folder, filename)
           print(file_path)
           c = conn.cursor()
           c.execute("""INSERT INTO SUBMISSION (USER_ID, LINK_TITLE, FILE_NAME, FILE_PATH, WEEK_NO, COURSE_ID, SESSION_NAME) VALUES(:a, :b, :c, :d, :e, :f, :g)""",
                     {"a" : curr_user,
                      "b" : link_title,
                      "c" : filename,
                      "d" : file_path,
                      "e" : week_number,
                      "f" : course_id,
                      "g" : session_name})
           conn.commit()
           c.close()
           file_uploaded = True
           c = conn.cursor()
           c.execute("""SELECT FILE_PATH, TO_CHAR(UPLOAD_TIME,'MM/DD/YYYY HH24:MI:SS'), FILE_NAME FROM SUBMISSION WHERE USER_ID = :a AND COURSE_ID = :b AND SESSION_NAME = :c AND WEEK_NO = :d AND LINK_TITLE = :e""",
                    {"a" : curr_user,
                     "b" : course_id,
                     "c" : session_name,
                     "d" : week_number,
                     "e" : link_title})
           result = c.fetchone()
           print(result)
           c.close()

           file_path = result[0]
           file_name = result[2]
           last_modified = result[1]
           #TO_CHAR(UPLOAD_TIME,'MM/DD/YYYY HH24:MI:SS'),

           submission_status = 'Submitted for grading'
           grading_status = 'Not graded'

           return render(request, 'basic_app/view_submission_link.html',
                        {'submission_status': submission_status, 'grading_status': grading_status,
                         'file_uploaded': file_uploaded, 'submission_details': submission_details,
                          'logged_in': logged_in, 'is_teacher': is_teacher,
                          'session_name' : session_name, 'course_id': course_id,
                          'week_number' : week_number, 'days':days, 'hours':hours,
                          'minutes':minutes, 'file_path':file_path, 'link_title':link_title,
                          'file_name':file_name, 'last_modified':last_modified})

       submission_status = 'No attempt'
       grading_status = 'Not graded'

       return render(request, 'basic_app/view_submission_link.html',
                    {'submission_status': submission_status, 'grading_status': grading_status,
                     'file_uploaded': file_uploaded, 'submission_details': submission_details,
                      'logged_in': logged_in, 'is_teacher': is_teacher,
                      'session_name' : session_name, 'course_id': course_id,
                      'week_number' : week_number, 'days':days, 'hours':hours,
                      'minutes':minutes, 'link_title':link_title})

def create_submission_link(request, session_name, course_id, week_number):
    user_id = curr_user
    if request.method == 'POST':
        link_title = request.POST.get('link_title')
        link_description = request.POST.get('description')
        due_date = request.POST.get('due_date')

        user_id = curr_user

        c = conn.cursor()
        c.execute("""INSERT INTO SUBMISSION_LINK VALUES(:a, :b, :c, :d, :e, :f, TO_DATE(:g, 'YYYY-MM-DD"T"HH24:MI'))""",
                  {"a" : user_id,
                   "b" : course_id,
                   "c" : session_name,
                   "d" : link_title,
                   "e" : link_description,
                   "f" : week_number,
                   "g" : due_date})
        conn.commit()
        c.close()

        return HttpResponseRedirect(reverse('course_week_details', args=(session_name, course_id, week_number)))
    return render(request, 'basic_app/create_submission_link.html',{'logged_in' : logged_in, 'session_name':session_name, 'course_id' : course_id, 'week_number':week_number, 'is_teacher':is_teacher})


def post_other_links(request, session_name, course_id, week_number):
    user_id = curr_user
    if request.method == 'POST':
        topic_name = request.POST.get('topic_name')
        link_address = request.POST.get('link_address')

        user_id = curr_user

        c = conn.cursor()
        c.execute("""INSERT INTO OTHER_LINKS VALUES(:a, :b, :c, :d, :e, :f)""",
                  {"a" : topic_name,
                   "b" : link_address,
                   "c" : course_id,
                   "d" : session_name,
                   "e" : week_number,
                   "f" : user_id})
        conn.commit()
        c.close()
        return HttpResponseRedirect(reverse('course_week_details', args=(session_name, course_id, week_number)))
    return render(request, 'basic_app/post_other_links.html',{'logged_in' : logged_in, 'session_name':session_name, 'course_id' : course_id, 'week_number':week_number, 'is_teacher':is_teacher})


def create_post(request, session_name, course_id):
    user_id = curr_user
    if request.method == 'POST':
        post_title = request.POST.get('post_title')
        post_description = request.POST.get('post_description')

        c = conn.cursor()
        c.execute("SELECT * FROM POST")
        result = c.fetchall()
        post_id = len(result)+1;
        c.close()
        user_id = curr_user

        c = conn.cursor()
        c.execute("""INSERT INTO POST VALUES(:a, :b, :c, :d, :e, :f)""",
                  {"a" : post_id,
                   "b" : user_id,
                   "c" : course_id,
                   "d" : session_name,
                   "e" : post_title,
                   "f" : post_description})
        conn.commit()
        c.close()
        return HttpResponseRedirect(reverse('course_details', args=(session_name, course_id)))
    return render(request, 'basic_app/create_post.html',{'logged_in' : logged_in, 'session_name':session_name, 'course_id' : course_id, 'is_teacher':is_teacher})

def show_post(request, session_name, course_id):
    c = conn.cursor()
    c.execute("""SELECT P.POST_TITLE, P.POST_DESCRIPTION, U.FIRST_NAME||' '||U.LAST_NAME, P.POST_ID FROM POST P, USER_DESCRIPTION U WHERE P.SESSION_NAME = :a AND P.COURSE_ID = :b AND P.USER_ID = U.USER_ID""",
             {"a" : session_name,
              "b" : course_id})
    result = c.fetchall()
    c.close()

    posts = []

    for r in result:
        post_title = r[0]
        post_description = r[1]
        user_id = r[2]
        post_id = r[3]
        row = {'post_title':post_title, 'post_description':post_description, 'user_id':user_id, 'post_id':post_id, 'logged_in':logged_in}
        posts.append(row)
    posts.reverse()
    return render(request,'basic_app/show_post.html',{'session_name':session_name, 'course_id' : course_id, 'is_teacher':is_teacher, 'logged_in' : logged_in, 'posts':posts})
def comments(request, post_id):
    if request.method == 'POST':
        comment_description = request.POST.get('comment_description')
        c = conn.cursor()
        c.execute("""INSERT INTO USER_POST_RELATION VALUES(:a, :b, :c)""",
                  {"a" : curr_user,
                   "b" : post_id,
                   "c" : comment_description})
        conn.commit()
        c.close()
        return HttpResponseRedirect(reverse('comments', args=(post_id)))
        #return render(request, 'basic_app/comments.html',{'post_id':post_id, 'logged_in':logged_in})

    c = conn.cursor()
    c.execute("""SELECT U.FIRST_NAME||' '||U.LAST_NAME, P.COMMENT_DESCRIPTION FROM USER_POST_RELATION P, USER_DESCRIPTION U WHERE P.POST_ID = :a AND P.USER_ID = U.USER_ID""",
             {"a" : post_id})
    result = c.fetchall()
    c.close()

    comments = []

    for r in result:
        user_id = r[0]
        comment_description = r[1]
        row = {'user_id':user_id, 'comment_description':comment_description}
        comments.append(row)
    return render(request,'basic_app/comments.html',{'post_id':post_id, 'comments':comments, 'logged_in':logged_in})

def course_week_details(request, session_name, course_id, week_number):
    c = conn.cursor()
    c.execute("""SELECT FILE_PATH, FILE_NAME FROM FILES WHERE SESSION_NAME = :a AND COURSE_ID = :b AND WEEK_NO = :c""",
             {"a" : session_name,
              "b" : course_id,
              "c" : week_number})
    result = c.fetchall()
    c.close()

    files = []

    for r in result:
        file_path = r[0]
        file_name = r[1]
        row = {'file_path':file_path, 'file_name':file_name}
        files.append(row)

    c = conn.cursor()
    c.execute("""SELECT TOPIC, LINK_ADDRESS FROM OTHER_LINKS WHERE SESSION_NAME = :a AND COURSE_ID = :b AND WEEK_NO = :c""",
             {"a" : session_name,
              "b" : course_id,
              "c" : week_number})
    result = c.fetchall()
    c.close()

    links = []

    for r in result:
        topic_name = r[0]
        link_address = r[1]
        row = {'topic_name':topic_name, 'link_address':link_address}
        links.append(row)

    c = conn.cursor()
    c.execute("""SELECT LINK_TITLE, DESCRIPTION FROM SUBMISSION_LINK WHERE COURSE_ID = :a AND SESSION_NAME = :b AND WEEK_NO = :c""",
              {"a" : course_id,
               "b" : session_name,
               "c" : week_number})
    result = c.fetchall()
    c.close()

    submission_links = []

    for r in result:
       link_title = r[0]
       description = r[1]
       row = {'link_title':link_title, 'description':description}
       submission_links.append(row)

    return render(request,'basic_app/week_view.html',{'session_name':session_name, 'course_id' : course_id, 'is_teacher':is_teacher, 'week_number':week_number, 'files':files, 'links':links, 'logged_in' : logged_in, 'submission_links' : submission_links})

def upload_file(request, session_name, course_id, week_number):
    if request.method == 'POST':
        user_id = curr_user
        user_folder = 'static/basic_app/files/'
        if not os.path.exists(user_folder):
            os.mkdir(user_folder)
        myfile = request.FILES['filename']
        filename = myfile.name
        print(filename)
        fs = FileSystemStorage(location=user_folder)

        filename = fs.save(filename, myfile)
        print(filename)
        #file_url = fs.url(filename)
        #print(file_url)
        file_path = os.path.join(user_folder, filename)
        print(file_path)
        c = conn.cursor()
        c.execute("""INSERT INTO FILES VALUES(:a, :b, :c, :d, :e, :f, SYSDATE)""",
                  {"a" : curr_user,
                   "b" : course_id,
                   "c" : session_name,
                   "d" : filename,
                   "e" : file_path,
                   "f" : week_number})
        conn.commit()
        c.close()
        return HttpResponseRedirect(reverse('course_week_details', args=(session_name, course_id, week_number)))

    return render(request,'basic_app/upload_file.html',{'logged_in' : logged_in, 'session_name':session_name, 'course_id' : course_id, 'is_teacher':is_teacher, 'week_number':week_number})

def user_logout(request):
    global logged_in
    logged_in = False
    #logout(request)
    #return HttpResponseRedirect(reverse('index'))
    return render(request, 'basic_app/index.html', {'logged_in' : logged_in})

def homepage(request):
    #logged_in = True

    print(logged_in)
    c = conn.cursor()
    c.execute("SELECT COURSE_ID, SESSION_NAME, COURSE_TITLE FROM COURSE")
    result = c.fetchall()
    c.close()

    courses = []

    for r in result:
        course_id = r[0]
        session_name = r[1]
        course_title = r[2]
        row = {'course_id':course_id, 'session_name':session_name, 'course_title':course_title}
        courses.append(row)

    return render(request,'basic_app/homepage.html',{'courses' : courses, 'logged_in' : logged_in})

def my_courses(request):
    #logged_in = True
    print(logged_in)

    c = conn.cursor()
    print(curr_user)
    if is_teacher == 1:
        c.execute("""SELECT COURSE_ID, SESSION_NAME FROM TEACHER_COURSE_RELATION WHERE USER_ID = :s""",
            {"s" : curr_user})
    else:
        c.execute("""SELECT COURSE_ID, SESSION_NAME FROM STUDENT_COURSE_RELATION WHERE USER_ID = :s""",
            {"s" : curr_user})
    print(curr_user)
    result = c.fetchall()
    c.close()

    courses = []

    for r in result:
        course_id = r[0]
        session_name = r[1]
        row = {'course_id':course_id, 'session_name':session_name}
        courses.append(row)

    return render(request,'basic_app/my_courses.html',{'courses' : courses, 'logged_in' : logged_in})

def course_details(request, session_name, course_id):
    c = conn.cursor()
    if(curr_user[0] == 'T'):
        c.execute("SELECT USER_ID FROM TEACHER_COURSE_RELATION WHERE USER_ID = :a AND SESSION_NAME = :b AND COURSE_ID = :c",
                  {"a" : curr_user,
                   "b" : session_name,
                   "c" : course_id})
    elif(curr_user[0] == 'S'):
        c.execute("SELECT USER_ID FROM STUDENT_COURSE_RELATION WHERE USER_ID = :a AND SESSION_NAME = :b AND COURSE_ID = :c",
                  {"a" : curr_user,
                   "b" : session_name,
                   "c" : course_id})
    result = c.fetchone()
    c.close()
    if(result != None):
        return render(request,'basic_app/week_page.html',{'session_name':session_name, 'course_id' : course_id, 'is_teacher':is_teacher, 'week_number':0, 'logged_in' : logged_in})
    else:
        not_enrolled = True
        return render(request,'basic_app/week_page.html',{'logged_in' : logged_in, 'not_enrolled' : not_enrolled})

def moodle_admin(request):
    return render(request, 'basic_app/moodle_admin.html', {'logged_in' : logged_in})

def user_desc_choice(request):
    return render(request, 'basic_app/user_desc_choice.html')

def user_desc_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM USER_DESCRIPTION")
    result = c.fetchall()
    c.close()

    user_description = []

    for r in result:
        user_id = r[0]
        password = r[1]
        first_name = r[2]
        last_name = r[3]
        country = r[4]
        city = r[5]
        profile_pic = r[6]
        row = {'user_id':user_id, 'first_name':first_name,
                'last_name':last_name, 'country':country, 'city':city, 'profile_pic':profile_pic}
        user_description.append(row)

    return render(request,'basic_app/list_users.html',{'user_description' : user_description})

def user_desc_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        country = request.POST.get('country')
        city = request.POST.get('city')
        '''print(user_id)
        print(password)
        print(first_name)
        print(last_name)
        print(country)
        print(city)'''

        hashed_password = pbkdf2_sha256.encrypt(password, rounds = 1200, salt_size = 32)
        #print(hashed_password)

        try:
            if(user_id[0] == 'T' or user_id[0] == 'S'):
                c = conn.cursor()
                #print("Hi")
                c.execute("INSERT INTO USER_DESCRIPTION(USER_ID, PASSWORD, FIRST_NAME, LAST_NAME, COUNTRY, CITY) VALUES(:a, :b, :c, :d, :e, :f)",
                            {"a" : user_id,
                             "b" : hashed_password,
                             "c" : first_name,
                             "d" : last_name,
                             "e" : country,
                             "f" : city})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                added_succesfully = True
                error = False

                return render(request, 'basic_app/add_users.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/add_users.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/add_users.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/add_users.html')

def user_desc_update(request):
    updated_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        #password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        country = request.POST.get('country')
        city = request.POST.get('city')
        '''print(user_id)
        print(password)
        print(first_name)
        print(last_name)
        print(country)
        print(city)'''

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM USER_DESCRIPTION WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None):
                c.execute("UPDATE USER_DESCRIPTION SET FIRST_NAME = :c, LAST_NAME = :d, COUNTRY = :e, CITY = :f WHERE USER_ID = :a",
                            {"a" : user_id,
                             "c" : first_name,
                             "d" : last_name,
                             "e" : country,
                             "f" : city})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                updated_succesfully = True
                error = False

                return render(request, 'basic_app/update_users.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/update_users.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/update_users.html',
                        {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/update_users.html')

def user_desc_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM USER_DESCRIPTION WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None):
                c.execute("""DELETE FROM USER_DESCRIPTION WHERE USER_ID = :a""",
                            {"a" : user_id})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_users.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/delete_users.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            #print("Hi")
            return render(request, 'basic_app/delete_users.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/delete_users.html')

def course_choice(request):
    return render(request, 'basic_app/course_choice.html')

def course_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM COURSE")
    result = c.fetchall()
    c.close()

    courses = []

    for r in result:
        course_id = r[0]
        session_name = r[1]
        course_title = r[2]
        credit_hour = r[3]
        row = {'course_id':course_id, 'session_name':session_name, 'course_title':course_title, 'credit_hour':credit_hour}
        courses.append(row)

    return render(request,'basic_app/list_courses.html',{'courses' : courses})

def courses_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        session_name = request.POST.get('session_name')
        course_title = request.POST.get('course_title')
        credit_hour = request.POST.get('credit_hour')

        try:
            c = conn.cursor()
            c.execute("INSERT INTO COURSE VALUES(:a, :b, :c, :d)",
                        {"a" : course_id,
                         "b" : session_name,
                         "c" : course_title,
                         "d" : credit_hour})
            #print("Hi")
            conn.commit()
            #result = c.fetchone()
            c.close()

            added_succesfully = True
            error = False

            return render(request, 'basic_app/add_courses.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name})
        except:
            return render(request, 'basic_app/add_courses.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name})

    else:
        return render(request, 'basic_app/add_courses.html')

def courses_update(request):
    updated_succesfully = False
    error = True

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        session_name = request.POST.get('session_name')
        course_title = request.POST.get('course_title')
        credit_hour = request.POST.get('credit_hour')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT SESSION_NAME, COURSE_ID FROM COURSE WHERE SESSION_NAME = :a AND COURSE_ID = :b""",
                        {"a" : session_name,
                         "b" : course_id})
            result = c.fetchone()
            if(result != None):
                c.execute("UPDATE COURSE SET COURSE_TITLE = :c, CREDIT_HOUR = :d WHERE SESSION_NAME = :a AND COURSE_ID = :b",
                            {"a" : session_name,
                             "b" : course_id,
                             "c" : course_title,
                             "d" : credit_hour})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                updated_succesfully = True
                error = False

                return render(request, 'basic_app/update_courses.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name})
            else:
                return render(request, 'basic_app/update_courses.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error})
        except:
            return render(request, 'basic_app/update_courses.html',
                        {'updated_succesfully' : updated_succesfully, 'error' : error})

    else:
        return render(request, 'basic_app/update_courses.html')

def courses_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        session_name = request.POST.get('session_name')
        course_id = request.POST.get('course_id')
        print(session_name)
        print(course_id)
        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT SESSION_NAME, COURSE_ID FROM COURSE WHERE SESSION_NAME = :a AND COURSE_ID = :b""",
                        {"a" : session_name,
                         "b" : course_id})
            result = c.fetchone()
            if(result != None):
                c.execute("""DELETE FROM COURSE WHERE SESSION_NAME = :a AND COURSE_ID = :b""",
                            {"a" : session_name,
                             "b" : course_id})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_courses.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name})
            else:
                print("error")
                return render(request, 'basic_app/delete_courses.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error})
        except:
            return render(request, 'basic_app/delete_courses.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error})

    else:
        return render(request, 'basic_app/delete_courses.html')

def student_choice(request):
    return render(request, 'basic_app/student_choice.html')

def student_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM STUDENT")
    result = c.fetchall()
    c.close()

    students = []

    for r in result:
        user_id = r[0]
        current_level = r[1]
        current_term = r[2]
        cgpa = r[3]
        row = {'user_id':user_id, 'current_level':current_level, 'current_term':current_term,
                'cgpa':cgpa}
        students.append(row)

    return render(request,'basic_app/list_students.html',{'students' : students})

def students_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        current_level = request.POST.get('current_level')
        current_term = request.POST.get('current_term')
        cgpa = request.POST.get('cgpa')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM USER_DESCRIPTION WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            print(result[0])
            if(result != None and result[0][0] == 'S'):
                c.execute("INSERT INTO STUDENT VALUES(:a, :b, :c, :d)",
                            {"a" : user_id,
                             "b" : current_level,
                             "c" : current_term,
                             "d" : cgpa})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                added_succesfully = True
                error = False

                return render(request, 'basic_app/add_students.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/add_students.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/add_students.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/add_students.html')

def students_update(request):
    updated_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        current_level = request.POST.get('current_level')
        current_term = request.POST.get('current_term')
        cgpa = request.POST.get('cgpa')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM STUDENT WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            print(result[0])
            if(result != None and result[0][0] == 'S'):
                c.execute("UPDATE STUDENT SET CURRENT_LEVEL = :b, CURRENT_TERM = :c, CGPA = :d WHERE USER_ID = :a",
                            {"a" : user_id,
                             "b" : current_level,
                             "c" : current_term,
                             "d" : cgpa})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                updated_succesfully = True
                error = False

                return render(request, 'basic_app/update_students.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/update_students.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/update_students.html',
                        {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/update_students.html')

def students_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM STUDENT WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None):
                c.execute("""DELETE FROM STUDENT WHERE USER_ID = :a""",
                            {"a" : user_id})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_students.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/delete_students.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            #print("Hi")
            return render(request, 'basic_app/delete_students.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/delete_students.html')

def teacher_choice(request):
    return render(request, 'basic_app/teacher_choice.html')

def teacher_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM TEACHER")
    result = c.fetchall()
    c.close()

    teachers = []

    for r in result:
        user_id = r[0]
        designation = r[1]
        room_number = r[2]
        row = {'user_id':user_id, 'designation':designation, 'room_number':room_number}
        teachers.append(row)

    return render(request,'basic_app/list_teachers.html',{'teachers' : teachers})

def teachers_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        designation = request.POST.get('designation')
        room_number = request.POST.get('room_number')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM USER_DESCRIPTION WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            print(result[0])
            if(result != None and result[0][0] == 'T'):
                c.execute("INSERT INTO TEACHER VALUES(:a, :b, :c)",
                            {"a" : user_id,
                             "b" : designation,
                             "c" : room_number})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                added_succesfully = True
                error = False

                return render(request, 'basic_app/add_teachers.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/add_teachers.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/add_teachers.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/add_teachers.html')

def teachers_update(request):
    updated_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        designation = request.POST.get('designation')
        room_number = request.POST.get('room_number')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM TEACHER WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            print(result[0])
            if(result != None and result[0][0] == 'T'):
                c.execute("UPDATE TEACHER SET DESIGNATION = :b, ROOM_NUMBER = :c WHERE USER_ID = :a",
                            {"a" : user_id,
                             "b" : designation,
                             "c" : room_number})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                updated_succesfully = True
                error = False

                return render(request, 'basic_app/update_teachers.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/update_teachers.html',
                            {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/update_teachers.html',
                        {'updated_succesfully' : updated_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/update_teachers.html')

def teachers_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM TEACHER WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None):
                c.execute("""DELETE FROM TEACHER WHERE USER_ID = :a""",
                            {"a" : user_id})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_teachers.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
            else:
                return render(request, 'basic_app/delete_teachers.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            #print("Hi")
            return render(request, 'basic_app/delete_teachers.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/delete_teachers.html')

def student_course_relation_choice(request):
    return render(request, 'basic_app/student_course_relation_choice.html')

def student_course_relation_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM STUDENT_COURSE_RELATION")
    result = c.fetchall()
    c.close()

    relations = []

    for r in result:
        user_id = r[0]
        course_id = r[1]
        session_name = r[2]
        row = {'user_id':user_id, 'course_id':course_id, 'session_name':session_name}
        relations.append(row)

    return render(request,'basic_app/list_student_course_relation.html',{'relations' : relations})

def student_course_relation_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        course_id = request.POST.get('course_id')
        session_name = request.POST.get('session_name')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM STUDENT WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None and result[0][0] == 'S'):
                c.execute("INSERT INTO STUDENT_COURSE_RELATION VALUES(:a, :b, :c)",
                            {"a" : user_id,
                             "b" : course_id,
                             "c" : session_name})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                added_succesfully = True
                error = False

                return render(request, 'basic_app/add_student_course_relation.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id, 'course_id' : course_id, 'session_name' : session_name})
            else:
                return render(request, 'basic_app/add_student_course_relation.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/add_student_course_relation.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/add_student_course_relation.html')

def student_course_relation_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        session_name = request.POST.get('session_name')
        course_id = request.POST.get('course_id')
        print(user_id)
        print(session_name)
        print(course_id)
        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT SESSION_NAME, COURSE_ID FROM STUDENT_COURSE_RELATION WHERE SESSION_NAME = :a AND COURSE_ID = :b AND USER_ID = :c""",
                        {"a" : session_name,
                         "b" : course_id,
                         "c" : user_id})
            print("HI")
            result = c.fetchone()
            print(result)
            if(result != None):
                c.execute("""DELETE FROM STUDENT_COURSE_RELATION WHERE SESSION_NAME = :a AND COURSE_ID = :b AND USER_ID = :c""",
                            {"a" : session_name,
                             "b" : course_id,
                             "c" : user_id})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_student_course_relation.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name, 'user_id' : user_id})
            else:
                print("error")
                return render(request, 'basic_app/delete_student_course_relation.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error})
        except:
            return render(request, 'basic_app/delete_student_course_relation.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error})

    else:
        return render(request, 'basic_app/delete_student_course_relation.html')

def teacher_course_relation_choice(request):
    return render(request, 'basic_app/teacher_course_relation_choice.html')

def teacher_course_relation_view(request):
    c = conn.cursor()
    c.execute("SELECT * FROM TEACHER_COURSE_RELATION")
    result = c.fetchall()
    c.close()

    relations = []

    for r in result:
        user_id = r[0]
        course_id = r[1]
        session_name = r[2]
        row = {'user_id':user_id, 'course_id':course_id, 'session_name':session_name}
        relations.append(row)

    return render(request,'basic_app/list_teacher_course_relation.html',{'relations' : relations})

def teacher_course_relation_add(request):
    added_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        course_id = request.POST.get('course_id')
        session_name = request.POST.get('session_name')

        try:
            c = conn.cursor()
            #print("Hi")
            c.execute("""SELECT USER_ID FROM TEACHER WHERE USER_ID = :a""",
                        {"a" : user_id})
            result = c.fetchone()
            if(result != None and result[0][0] == 'T'):
                c.execute("INSERT INTO TEACHER_COURSE_RELATION VALUES(:a, :b, :c)",
                            {"a" : user_id,
                             "b" : course_id,
                             "c" : session_name})
                #print("Hi")
                conn.commit()
                #result = c.fetchone()
                c.close()

                added_succesfully = True
                error = False

                return render(request, 'basic_app/add_teacher_course_relation.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id, 'course_id' : course_id, 'session_name' : session_name})
            else:
                return render(request, 'basic_app/add_teacher_course_relation.html',
                            {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})
        except:
            return render(request, 'basic_app/add_teacher_course_relation.html',
                        {'added_succesfully' : added_succesfully, 'error' : error, 'user_id' : user_id})

    else:
        return render(request, 'basic_app/add_teacher_course_relation.html')

def teacher_course_relation_delete(request):
    deleted_succesfully = False
    error = True

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        session_name = request.POST.get('session_name')
        course_id = request.POST.get('course_id')
        print(user_id)
        print(session_name)
        print(course_id)
        try:
            c = conn.cursor()
            c.execute("""SELECT SESSION_NAME, COURSE_ID FROM TEACHER_COURSE_RELATION WHERE SESSION_NAME = :a AND COURSE_ID = :b AND USER_ID = :c""",
                        {"a" : session_name,
                         "b" : course_id,
                         "c" : user_id})
            result = c.fetchone()
            print(result)
            if(result != None):
                c.execute("""DELETE FROM TEACHER_COURSE_RELATION WHERE SESSION_NAME = :a AND COURSE_ID = :b AND USER_ID = :c""",
                            {"a" : session_name,
                             "b" : course_id,
                             "c" : user_id})
                conn.commit()
                c.close()

                deleted_succesfully = True
                error = False

                return render(request, 'basic_app/delete_teacher_course_relation.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error, 'course_id' : course_id, 'session_name' : session_name, 'user_id' : user_id})
            else:
                print("error")
                return render(request, 'basic_app/delete_teacher_course_relation.html',
                            {'deleted_succesfully' : deleted_succesfully, 'error' : error})
        except:
            return render(request, 'basic_app/delete_teacher_course_relation.html',
                        {'deleted_succesfully' : deleted_succesfully, 'error' : error})

    else:
        return render(request, 'basic_app/delete_teacher_course_relation.html')

def user_login(request):

    if request.method == 'POST':
        not_logged_in = False
        #logged_in = True
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            c = conn.cursor()
            #sql = " SELECT PASSWORD FROM USER_DESCRIPTION WHERE USER_ID = %s ;"
            c.execute("""SELECT PASSWORD FROM USER_DESCRIPTION WHERE USER_ID = :s""",
                     {"s" : username})
            result = c.fetchone()
            c.close()

            if(pbkdf2_sha256.verify(password, result[0])):
                global curr_user, is_teacher
                curr_user = username
                if(curr_user[0]=='T'):
                    is_teacher = 1
                else:
                    is_teacher = 0

                global logged_in
                logged_in = True
                #return HttpResponseRedirect(reverse('index'))
                #return render(request, 'basic_app/homepage.html', {'courses':courses, 'logged_in':logged_in})
                return HttpResponseRedirect(reverse('basic_app:homepage'))
            else:
                not_logged_in = True
                return render(request, 'basic_app/login.html', {'not_logged_in':not_logged_in})

        except:
            not_logged_in = True
            messages = "Log in failed"
            print(messages)
            return render(request,'basic_app/login.html', {'not_logged_in':not_logged_in})

    else:
        return render(request, 'basic_app/login.html', {'logged_in':logged_in})
