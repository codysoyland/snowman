from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from repocracy.repo import tasks
import hashlib

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

    @classmethod
    def is_pending(cls, repo):
        return repo.status < cls.READY 

class RepoTypes(Choices):
    GIT = 0
    HG = 1

    @classmethod
    def get_typename(cls, repo):
        return ['git', 'hg'][repo.origin_type]

class Repository(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    origin_type = models.IntegerField(choices=Status.as_choices(), default=0)
    fs_path = models.CharField(max_length=255)
    status = models.IntegerField(choices=RepoTypes.as_choices(), default=0)
    claim_hash = models.CharField(max_length=40, default=lambda : hashlib.sha1().hexdigest())

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
        name = name.rsplit('.', 1)[0]
        return name

    def is_bitbucket(self):
        """
        Return True if our `origin` is a bitbucket URL.
        """
        return self.origin_type == RepoTypes.HG and re.search(r'.*bitbucket\.org', self.origin)

    def is_github(self):
        """
        Return True if our `origin` is a github URL.
        """
        return self.origin_type == RepoTypes.GIT and re.search(r'.*github\.com', self.origin)

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={
            'name':slugify(self.get_name()),
        })

    def update(self):
        return getattr(tasks, 'pull_%s' % RepoTypes.get_typename(self)).delay(self.pk)

    def get_claim_url(self):
        return reverse('repo_claim', kwargs={
            'pk':self.pk,
            'claim_hash':self.claim_hash
        })

