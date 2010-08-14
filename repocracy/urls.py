from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    ('^bluebird/', include('bluebird.urls')),
    (r'', include('repocracy.repo.urls')),
)
