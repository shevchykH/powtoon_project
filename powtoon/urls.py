from django.conf.urls import url

from powtoon import views

urlpatterns = [
    url(r'^powtoons/$', views.PowtoonListView.as_view()),
    url(r'^powtoons/(?P<pk>\d+)/$', views.PowtoonDetailView.as_view()),
    url(r'^powtoons/(?P<pk>[0-9]+)/share/(?P<user_id>[0-9]+)/$', views.SharePowtoonView.as_view()),
    url(r'^shared_powtoons/$', views.SharedPowtoonList.as_view()),
]
