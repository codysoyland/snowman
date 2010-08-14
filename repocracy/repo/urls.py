from django.conf.urls.defaults import *

urlpatterns = patterns('repocracy.repo.views',
    url(r'^$', 'home', name='home'),
    url(r'^claim/(?P<pk>\d+)/(?P<claim_hash>[a-fA-F\d]{40})/$', 'repo_claim', name='repo_claim'),
    url(r'^repos/(?P<name>[/\-_\d\w\\\.]+)/$', 'repo_detail', name='repo_detail'),
    url(r'^post-receive/(?P<pk>\d+)/$', 'post_receive', name='post_receive'),
    url(r'^status/(?P<pk>\d+)/$', 'repo_status', name='repo_status'),
)
