"""Community URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import xadmin
from .settings import DEBUG, MEDIA_ROOT, BASE_DIR

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^', include('home.urls')),
    url(r'^forum/', include('home.urls')),
    url(r'^user/', include('home.urls')),
    url(r'^news/', include('home.urls')),
    url(r'^announcement/', include('home.urls')),
]

from django.views.static import serve
if DEBUG:
    urlpatterns+=url(r'^media/(?P<path>.*)/$', serve, {"document_root": MEDIA_ROOT}),
    # urlpatterns+=url(r'^upload /(?P<path>(\S)*)', serve, {'document_root': BASE_DIR+'/upload'}),

