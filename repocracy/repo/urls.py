from django.conf.urls.defaults import *

urlpatterns = patterns('repocracy.repo.views',
    url(r'^$', 'home', name='home'),
    url(r'^claim/(?P<pk>\d+)/(?P<claim_hash>[a-fA-F\d]{40})/$', 'repo_claim', name='repo_claim'),
    url(r'^repos/(?P<name>[/\-_\d\w\\\.]+)/$', 'repo_detail', name='repo_detail'),
)
