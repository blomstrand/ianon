from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.mainPage, name="main"),
	url(r'^texts/$', views.texts, name='texts'),
	url('^upload/$', views.upload, name='upload'),
	url('^edit/(?P<doc_id>[0-9]+)/$', views.edit, name='edit')
]