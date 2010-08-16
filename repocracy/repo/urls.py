from django.conf.urls.defaults import *
from django.conf import settings
import os

urlpatterns = patterns('repocracy.repo.views',
    url(r'^$', 'home', name='home'),
    url(r'^claim/(?P<pk>\d+)/(?P<claim_hash>[a-fA-F\d]{40})/$', 'repo_claim', name='repo_claim'),
    url(r'^users/(?P<name>[\-_\d\w\\\.]+)/$', 'repo_owner', name='repo_owner'),
    url(r'^repos/(?P<name>[/\-_\d\w\\\.]+)/$', 'repo_detail', name='repo_detail'),
    url(r'^post-receive/(?P<pk>\d+)/$', 'post_receive', name='post_receive'),
    url(r'^status/(?P<pk>\d+)/$', 'repo_status', name='repo_status'),
)

urlpatterns += patterns('',
    # Not a smart way to serve repos (very slow).
    # Serve with nginx using static http, or preferably the CGI hgwebdir script
    url(r'^hg(?P<path>.*)$', 'django.views.static.serve',
        {'show_indexes': True, 'document_root': os.path.join(settings.REPOCRACY_BASE_REPO_PATH, 'public_hg')}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'redirect_field_name': 'next'}),
)
