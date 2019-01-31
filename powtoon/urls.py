from django.conf.urls import url

from powtoon import views

urlpatterns = [
    url(r'^powtoons/$', views.PowtoonListView.as_view(), name="list"),
    url(r'^powtoons/(?P<pk>\d+)/$', views.PowtoonDetailView.as_view()),
    url(r'^powtoons/(?P<pk>\d+)/share/$', views.SharePowtoonView.as_view()),
    url(r'^shared_powtoons/$', views.SharedPowtoonList.as_view()),
]
