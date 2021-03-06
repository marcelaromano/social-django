"""polls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about/$', views.about, name='about'),
    url(r'^results/$', views.results, name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^facebook/(?P<page_id>\w+)/$', views.facebook_fanpage, name='facebook_fanpage'),
    url(r'^saludo/$', views.saludo, name='saludo'),
    url(r'^researcher/results/(?P<website_ids>[0-9,]+)/$', views.researcher_results_by_website, name='researcher_results_by_website'),
    url(r'^researcher/results/$', views.researcher_results, name='researcher_results'),
    url(r'^researcher/$', views.researcher, name='researcher'),
]
