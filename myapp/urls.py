from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signout$', views.signout, name='signout'),
    url(r'^signin$', views.signin, name='signin'),
    url(r'^headerSignIn/$', views.headerSignIn, name='headerSignIn'),
    url(r'^compareUser/', views.compareUser, name='compareUser'),
    url(r'^genRoutine/', views.genRoutine, name='genRoutine')
]