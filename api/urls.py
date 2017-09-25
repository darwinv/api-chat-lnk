from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^clients/$', views.ClientView.as_view(), name='clients'),
    url(r'^categorys/$', views.CategoryView.as_view(), name='categorys'),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]
