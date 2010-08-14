from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from repocracy.repo.models import Repository
from repocracy.repo.forms import NewRepoForm

def home(request):
    """
    Home page view. Form for entry of new repository.
    """
    form = NewRepoForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            repo = form.save()
            return HttpResponseRedirect(reverse('repo_detail', kwargs={'pk': repo.pk}))

    return render_to_response('home.html', {
            'form': form
        }, context_instance=RequestContext(request))

def repo_detail(request, pk):
    """
    Repository detail view. Renders `repo_pending.html` or
    `repo_detail.html` depending on status.
    """
    repo = get_object_or_404(Repository.objects.all(), pk=pk)

    # TODO: better status checking?
    if repo.status < 3:
        return render_to_response(
            'repo_pending.html',
            {},
            context_instance=RequestContext(request))

    return render_to_response('repo_detail.html', {
        }, context_instance=RequestContext(request))
