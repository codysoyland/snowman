from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from repocracy.repo.models import Repository, Status
from repocracy.repo.forms import NewRepoForm, RemoteForm
from repocracy.repo.tasks import push_to_remotes

CAN_CLAIM_KEY = 'claim_repo'

def home(request):
    """
    Home page view. Form for entry of new repository.
    """
    form = NewRepoForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            repo = form.save(request.user)
            request.session[CAN_CLAIM_KEY] = repo.pk 
            return redirect(repo)

    return render_to_response('home.html', {
            'form': form
        }, context_instance=RequestContext(request))

def repo_detail(request, name):
    """
    Repository detail view. Renders `repo_pending.html` or
    `repo_detail.html` depending on status.
    """
    repo = get_object_or_404(Repository.objects.all(), slug=name)

    remote_form = RemoteForm(request.POST or None)
    if request.POST:
        if remote_form.is_valid():
            instance = remote_form.save(commit=False)
            instance.repository = repo
            instance.save()
            push_to_remotes(repo.pk)

    context_dict = {
        'repo': repo,
        'site': Site.objects.get_current(),
        'can_claim':request.session.get(CAN_CLAIM_KEY, None) == repo.pk,
        'remote_form': remote_form,
    }

    return render_to_response(
        'repo_pending.html' if Status.is_pending(repo) else 'repo_detail.html',
        context_dict, context_instance=RequestContext(request))

def repo_claim(request, pk, claim_hash):
    """
    Use hash from repo (in twitter redirect URL) to "claim" the repo (assign
    your user object to it).
    """
    if request.user.is_authenticated():
        repo = get_object_or_404(Repository, pk=int(pk), claim_hash=claim_hash, user__pk__isnull=True)
        repo.user = request.user
        repo.slug = repo.get_slug()
        repo.save()
        repo.build_symlinks()
        return redirect(repo)
    return redirect('home')

def repo_status(request, pk):
    repo = get_object_or_404(Repository, pk=pk)
    return HttpResponse(simplejson.dumps({
        'repo_url':repo.get_absolute_url(),
        'status':repo.status
    }), content_type='application/json')

@csrf_exempt
def post_receive(request, pk):
    """
    Post-receive hook for Github/Bitbucket/whatever.
    """
    repo = get_object_or_404(Repository, pk=pk)
    repo.update()
    return HttpResponse()

def repo_owner(request, name):
    user = get_object_or_404(User, username=name)
    return render_to_response('repo_owner.html', {
        'repo_owner':user
    }, context_instance=RequestContext(request))

