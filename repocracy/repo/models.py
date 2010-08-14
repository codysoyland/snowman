from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

REPOTYPES = (
    (0, 'git'),
    (1, 'hg'),
)

class Repository(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    origin_type = models.IntegerField(choices=REPOTYPES)
    fs_path = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def get_name(self):
        username = '' if self.user is None else self.user.username
        return '/'.join([i for i in [username, self.name] if i])

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={
            'name':slugify(self.get_name()),
        })
