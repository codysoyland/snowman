from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import hashlib
import os

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
    slug = models.SlugField(max_length=255, unique=True)
    origin = models.CharField(max_length=255)
    origin_type = models.IntegerField(choices=Status.as_choices(), default=0)
    fs_path = models.CharField(max_length=255)
    status = models.IntegerField(choices=RepoTypes.as_choices(), default=0)
    claim_hash = models.CharField(max_length=40, default=lambda : hashlib.sha1().hexdigest())

    def __unicode__(self):
        return self.name

    def get_slug(self):
        """
        Get name of repo to build repo url.
        """
        slug = None
        username = '' if self.user is None else slugify(self.user.username)
        trial = base_trial = '/'.join([i for i in [username, slugify(self.name)] if i])
        appended_number = 1
        while not slug:
            # Append number to trial if slug exists
            if Repository.objects.filter(slug=trial).count() > 0:
                trial = base_trial + unicode(appended_number)
                appended_number += 1
            else:
                slug = trial

        return slug

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
            'name':self.slug,
        })

    def update(self):
        from repocracy.repo import tasks
        return getattr(tasks, 'pull_%s' % RepoTypes.get_typename(self)).delay(self.pk)

    def get_claim_url(self):
        return reverse('repo_claim', kwargs={
            'pk':self.pk,
            'claim_hash':self.claim_hash
        })

    def build_symlinks(self):
        """
        Symlink primary git/hg urls to public_git and public_hg directories for public serving.
        """
        for vcs in ['git', 'hg']:
            public_vcs_path = os.path.join(settings.REPOCRACY_BASE_REPO_PATH, 'public_%s' % vcs)
            if not os.path.exists(public_vcs_path):
                os.makedirs(public_vcs_path)
            vcs_path = os.path.join(self.fs_path, vcs)

            destinations = [unicode(self.pk), self.slug]
            for path in destinations:
                if vcs == 'git':
                    path += '.git'

                os.symlink(vcs_path, os.path.join(public_vcs_path, path))

    def get_vcs_uri(self, vcs):
        """
        Get VCS url for given VCS.
        """
        if vcs == 'git':
            return 'git://repocracy.com/%s.git' % self.slug
        elif vcs == 'hg':
            return 'http://repocracy.com/hg/%s/' % self.slug

    @property
    def git_uri(self):
        return self.get_vcs_uri('git')

    @property
    def hg_uri(self):
        return self.get_vcs_uri('hg')
