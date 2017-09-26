from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^clients/$', views.ClientListView.as_view(), name='clients'),
    url(r'^clients/(?P<pk>[0-9]+)/$', views.ClientDetailView.as_view(), name='client-detail'),
    url(r'^categorys/$', views.CategoryListView.as_view(), name='categorys'),
    url(r'^categorys/(?P<pk>[0-9]+)/$', views.CategoryDetailView.as_view(), name='category-detail'),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]
