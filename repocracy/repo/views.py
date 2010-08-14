from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from repocracy.repo.models import Repository, Status
from repocracy.repo.forms import NewRepoForm

def home(request):
    """
    Home page view. Form for entry of new repository.
    """
    form = NewRepoForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            repo = form.save()
            return redirect(repo)

    return render_to_response('home.html', {
            'form': form
        }, context_instance=RequestContext(request))

def repo_detail(request, name):
    """
    Repository detail view. Renders `repo_pending.html` or
    `repo_detail.html` depending on status.
    """
    username, reponame = name.split('/', 1) if '/' in name else (None, name) 
    base_filter = {'user__username':username} if username else {} 
    repo = get_object_or_404(Repository.objects.filter(**base_filter), name=reponame)

    # TODO: better status checking?
    if Status.is_pending(repo):
        return render_to_response(
            'repo_pending.html',
            {'repo':repo},
            context_instance=RequestContext(request))

    return render_to_response('repo_detail.html', {
        }, context_instance=RequestContext(request))

def repo_claim(request, pk, claim_hash):
    if request.user.is_authenticated():
        repo = get_object_or_404(Repository, pk=int(pk), claim_hash=claim_hash, user__pk__isnull=True)
        repo.user = request.user
        repo.save()
        return redirect(repo)
    return redirect('home')
