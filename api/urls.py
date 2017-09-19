from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^client/$', views.Client.as_view()),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]
