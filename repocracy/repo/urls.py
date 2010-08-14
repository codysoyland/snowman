from django.conf.urls.defaults import *

urlpatterns = patterns('repocracy.repo.views',
    url(r'^$', 'home', name='home'),
    url(r'^repos/(?P<pk>\d+)/$', 'repo_detail', name='repo_detail'),
)
