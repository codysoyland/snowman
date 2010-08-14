from django.forms import ModelForm

from repocracy.repo.models import Repository

class NewRepoForm(ModelForm):
    class Meta:
        model = Repository
        fields = ('origin',)
