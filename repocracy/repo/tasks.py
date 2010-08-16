import os
import subprocess
import sys

from django.conf import settings
from celery.decorators import task

from repocracy.repo.models import Repository, Remote, Status, RepoTypes
import mercurial.ui
import mercurial.localrepo
from mercurial.commands import pull
from mercurial.commands import update
import hggit
import pexpect
import shutil

def update_git_master(hg_path, git_path, tip_hex):
    hggitmap = os.path.join(hg_path, 'git-mapfile')
    githead = os.path.join(git_path, 'refs', 'heads', 'master')
    with open(hggitmap, 'r') as input:
        for line in input:
            githash, hghash = line.split(' ')
            hghash = hghash.strip()
            if hghash == tip_hex:
                with open(githead, 'w') as output:
                    output.write(githash)
                break

@task
def push_to_remotes(repo_pk, auto_only=True):
    try:
        repo = Repository.objects.get(pk=repo_pk) 
    except Repository.DoesNotExist:
        return "Repository with %d did not exist. )`:" % repo_pk 

    remotes = Remote.objects.filter(repository=repo)
    if auto_only:
        remotes = remotes.filter(auto_push=True)

    for remote in remotes:
        repo_type = 'git' if remote.type == 0 else 'hg'
        if repo_type == 'git':
            result = subprocess.call(
                args=['git','push',remote.remote_url,'master'],
                cwd=os.path.join(repo.fs_path, 'git')
            )
        else:
            result = subprocess.call(
                args=['hg','push',remote.remote_url],
                cwd=os.path.join(repo.fs_path, 'hg')
            )

@task
def translate_repository(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk) 
    except Repository.DoesNotExist:
        return "Repository with %d did not exist. )`:" % repo_pk 
    Repository.objects.filter(pk=repo_pk).update(status=Status.PROCESSING)
    try:
        if repo.origin_type == RepoTypes.HG:

            hgui = mercurial.ui.ui()
            hgui.setconfig('git', 'intree', 'true')
            hgui.setconfig('git', 'exportbranch', 'refs/heads/master')

            hgpath = os.path.join(repo.fs_path, 'hg') 
            hgrepo = mercurial.localrepo.localrepository(hgui, hgpath)
            githandler = hggit.GitHandler(hgrepo, hgui)
            githandler.export_commits()

            tip_changeset = hgrepo['tip']
            tip_hex = tip_changeset.hex()
            hgrepopath = os.path.join(hgpath, '.hg')
            gitrepopath = os.path.join(hgpath, '.git')
            update_git_master(hgrepopath, gitrepopath, tip_hex)

            result = subprocess.call(
                args=['git','clone','--mirror', hgpath, './'],
                cwd=os.path.join(repo.fs_path, 'git')
            )

            
            if result == 0:
                shutil.rmtree(gitrepopath)
                symlink_target = os.path.join(hgpath, '.hg', 'git')
                if not os.path.exists(symlink_target):
                    os.symlink(os.path.join(repo.fs_path, 'git'), symlink_target)
                    repo.status = Status.READY
                    repo.save()
            else:
                repo.status = Status.ERROR
                repo.save()
        elif repo.origin_type == RepoTypes.GIT:
            hgui = mercurial.ui.ui()
            hgui.setconfig('git', 'intree', 'false')
            hgui.setconfig('git', 'exportbranch', 'refs/heads/master')
            hgpath = os.path.join(repo.fs_path, 'hg') 
            creation = 0 if os.path.exists(os.path.join(hgpath, '.hg')) else 1
            gitpath = os.path.join(repo.fs_path, 'git')
            hgrepo = mercurial.localrepo.localrepository(hgui, hgpath, creation)
            symlink_target = os.path.join(hgpath, '.hg', 'git')
            if not os.path.exists(symlink_target):
                os.symlink(gitpath, symlink_target)
            githandler = hggit.GitHandler(hgrepo, hgui)
            githandler.import_commits(None)
            repo.status = Status.READY
            repo.save()
        else:
            pass

        repo.build_symlinks()

        push_to_remotes(repo.pk)
    except Exception, e:
        Repository.objects.filter(pk=repo_pk).update(status=Status.ERROR)
        raise e
    finally:
        pass

@task
def pull_git(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk)
    except Repository.DoesNotExist:
        return
    git_dir = os.path.join(repo.fs_path, 'git')
    result = subprocess.call(
        args=['git','fetch','origin','master'], cwd=git_dir)
    result = result or subprocess.call(
        args=['git','reset','--soft','FETCH_HEAD'], cwd=git_dir)
    if result == 0:
        hgui = mercurial.ui.ui()
        hgui.setconfig('git', 'intree', 'false')
        hgpath = os.path.join(repo.fs_path, 'hg')
        hgrepo = mercurial.localrepo.localrepository(hgui, hgpath, 0)
        githandler = hggit.GitHandler(hgrepo, hgui)
        githandler.import_commits(None)

    push_to_remotes.delay(repo.pk, auto_only=True)

@task
def pull_hg(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk)
    except Repository.DoesNotExist:
        return
    hgpath = os.path.join(repo.fs_path, 'hg')

    for command in ['pull', 'update']:
        subprocess.call(args=['hg', command], cwd=hgpath)

    hgui = mercurial.ui.ui()
    hgui.setconfig('git', 'intree', 'false')
    hgrepo = mercurial.localrepo.localrepository(hgui, hgpath, 0)
    githandler = hggit.GitHandler(hgrepo, hgui)
    githandler.export_commits()

    tip_changeset = hgrepo['tip']
    tip_hex = tip_changeset.hex()
    gitrepopath = os.path.join(repo.fs_path, 'git')
    hgrepopath = os.path.join(hgpath, '.hg')
    update_git_master(hgrepopath, gitrepopath, tip_hex)

    push_to_remotes.delay(repo.pk, auto_only=True)

@task
def clone_repository(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk) 
    except Repository.DoesNotExist:
        pass
    else:
        destination = os.path.join(
            settings.REPOCRACY_BASE_REPO_PATH,
            unicode(repo.pk)
        )
        destination_dirs = [os.path.join(destination, type) for type in ('hg', 'git')]
        for i in destination_dirs:
            os.makedirs(i)

        child = pexpect.spawn(
            'git --git-dir=. clone --mirror %s .' % repo.origin,
            cwd=destination_dirs[1],
            timeout=None
        )
        result = child.expect([pexpect.EOF, 'Password:', 'hung up unexpectedly', 'fatal'])

        child.close()
        if result != 0:
            result = subprocess.call(
                args=['hg', 'clone', repo.origin, '.'],
                cwd=destination_dirs[0]
            )
            if result == 0: 
                repo.origin_type = RepoTypes.HG 
                repo.status = Status.CLONED 
            else:
                repo.status = Status.ERROR 
        else:
            repo.origin_type = RepoTypes.GIT 
            repo.status = Status.CLONED
        repo.fs_path = destination 
        repo.save()
        translate_repository.delay(repo.pk)
