import os
import subprocess
import sys

from django.conf import settings
from celery.decorators import task

from repocracy.repo.models import Repository, Status, RepoTypes
import mercurial.ui
import mercurial.localrepo
from mercurial.commands import pull
import hggit
import pexpect
import shutil

@task
def translate_repository(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk) 
    except Repository.DoesNotExist:
        return "Repository with %d did not exist. )`:" % repo_pk 
    Repository.objects.filter(pk=repo_pk).update(status=Status.PROCESSING)
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
        hggitmap = os.path.join(hgrepopath, 'git-mapfile')
        
        gitrepopath = os.path.join(hgpath, '.git')
        githead = os.path.join(gitrepopath, 'refs', 'heads', 'master')

        with open(hggitmap, 'r') as input:
            for line in input:
                githash, hghash = line.split(' ')
                hghash = hghash.strip()
                if hghash == tip_hex:
                    with open(githead, 'w') as output:
                        output.write(githash)
                    break
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

@task
def pull_hg(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk)
    except Repository.DoesNotExist:
        return
    hgui = mercurial.ui.ui()
    hgui.setconfig('git', 'intree', 'false')
    hgpath = os.path.join(repo.fs_path, 'hg')
    hgrepo = mercurial.localrepo.localrepository(hgui, hgpath, 0)
    try:
        pull(hgui, hgrepo)
    except:
        pass
    else:
        githandler = hggit.GitHandler(hgrepo, hgui)
        githandler.export_commits(None)

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
        )
        result = child.expect([pexpect.EOF, 'Password:', 'hung up unexpectedly', 'fatal'])

        #if result == 0:
        #    # clone was successful
        #elif result == 1:
        #    # password was asked for
        #elif result == 2:
        #    # problem with server

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
