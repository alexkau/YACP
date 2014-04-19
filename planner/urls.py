from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^upload_capp$', views.addCoursesTaken, name='addCoursesTaken'),
    url(r'^move_course$', views.moveCourse, name='moveCourse'),
    url(r'^add_course$', views.addCourse, name='addCourse'),
)
