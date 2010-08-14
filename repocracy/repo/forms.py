from django.forms import ModelForm

from repocracy.repo.models import Repository

class NewRepoForm(ModelForm):
    def save(self):
        obj = super(NewRepoForm, self).save(commit=False)
        obj.name = obj.guess_name()
        obj.save()
        return obj

    class Meta:
        model = Repository
        fields = ('origin',)
