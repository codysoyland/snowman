from django.forms import ModelForm

from repocracy.repo.models import Repository
from repocracy.repo.tasks import clone_repository

class NewRepoForm(ModelForm):
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
