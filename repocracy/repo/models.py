from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class Choices(object):
    @classmethod
    def as_choices(cls):
        returning = [(getattr(cls, i), i) for i in dir(cls) if isinstance(getattr(cls, i), int)]
        returning.sort()
        return returning


class Status(Choices):
    PENDING = 0
    CLONED = 1
    PROCESSING = 2
    READY = 3
    ERROR = 255


class RepoTypes(Choices):
    GIT = 0
    HG = 1


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
        """
        Get name of repo to build repo url.
        """
        username = '' if self.user is None else self.user.username
        return '/'.join([i for i in [username, self.name] if i])

    def guess_name(self):
        """
        Guess name of repository by examining origin url.

        Example:

        >>> self.origin = git://github.com/codysoyland/snowman.git
        >>> print self.guess_name()
        snowman
        """
        pieces = self.origin.split('/')
        name = pieces[-1]
        if not name:
            name = pieces[-2]
        name = name.split('.')[0]
        return name

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={
            'name':slugify(self.get_name()),
        })
