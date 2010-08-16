from django import forms
from django.conf import settings

from repocracy.repo.models import Repository, Remote, RemoteHost
from repocracy.repo.tasks import clone_repository

class NewRepoForm(forms.ModelForm):
    def clean_origin(self):
        data = self.cleaned_data['origin']
        if data[0] == '/':
            raise forms.ValidationError('Missing protocol.')
        if '@' in data:
            raise forms.ValidationError('"@" not allowed in origin URI.')
        if ';' in data:
            raise forms.ValidationError('Invalid origin URI (contains ";").')

        # Always return the cleaned data, whether you have changed it or
        # not.
        return data

    def save(self, user):
        obj = super(NewRepoForm, self).save(commit=False)
        obj.name = obj.guess_name()
        if user.is_authenticated():
            obj.user = user

        obj.slug = obj.get_slug()
        obj.save()
        clone_repository.delay(obj.pk)
        return obj

    class Meta:
        model = Repository
        fields = ('origin',)

class RemoteForm(forms.ModelForm):
    username = forms.CharField(max_length=255)
    repo_name = forms.CharField(max_length=255)
    remote_url = forms.CharField(max_length=255, required=False)
    type = forms.IntegerField(widget=forms.RadioSelect(choices=((0, 'Github'), (1, 'Bitbucket'))))
    def clean(self):
        if self.cleaned_data['type'] == 0:
            template = 'git@github.com:%s/%s.git'
        elif self.cleaned_data['type'] == 1:
            template = 'ssh://hg@bitbucket.org/%s/%s'

        self.cleaned_data['remote_url'] = template % (
            self.cleaned_data['username'], self.cleaned_data['repo_name'])
        return self.cleaned_data

    class Meta:
        model = Remote
        fields = ('remote_url', 'type', 'auto_push')
