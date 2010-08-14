from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class Status(object):
    PENDING = 0
    CLONED = 1
    PROCESSING = 2
    READY = 3
    ERROR = 255

    @classmethod
    def as_choices(cls):
        returning = [(getattr(cls, i), i) for i in dir(cls) if isinstance(getattr(cls, i), int)]
        returning.sort()
        return returning

class RepoTypes(object):
    GIT = 0
    HG = 1

    @classmethod
    def as_choices(cls):
        returning = [(getattr(cls, i), i) for i in dir(cls) if isinstance(getattr(cls, i), int)]
        returning.sort()
        return returning

class Repository(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    origin_type = models.IntegerField(choices=Status.as_choices(), default=0)
    fs_path = models.CharField(max_length=255)
    status = models.IntegerField(choices=RepoTypes.as_choices(), default=0)

    def __unicode__(self):
        return self.name

    def get_name(self):
        username = '' if self.user is None else self.user.username
        return '/'.join([i for i in [username, self.name] if i])

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={
            'name':slugify(self.get_name()),
        })

