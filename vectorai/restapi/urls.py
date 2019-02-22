
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/$', views.UploadFile.as_view()),
    url(r'^check/$', views.CheckUpload.as_view()),
    url(r'^check/(?P<filename>([a-zA-Z0-9\s_\\.\-\(\):])+(.png|.jpg)+)/$', views.CheckPassport.as_view()),
]