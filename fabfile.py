import os
import json
import subprocess
import shlex
import time
import signal
import urllib2

from fabric.api import run, local, settings, cd, sudo, task, output, puts
from fabric.contrib.project import upload_project
from fabric.contrib.files import append, upload_template


APPS = 'api courses courses_viz scheduler'.split(' ')

USER = 'www-data'
GROUP = 'www-data'

# we're using postgres!
# change to whatever you need to use
ADDITIONAL_PACKAGES = 'psycopg2'


PYTHON = '/www/yacs/virtualenv/bin/python'
PIP = '/www/yacs/virtualenv/bin/pip'


@task
def verbose():
    output['everything'] = True


def exists(name):
    with settings(warn_only=True):
        return not run('[ -e "%s" ]' % name).failed


def remote_vars(*keys):
    sb = []
    for key in keys:
        value = run('echo $' + key).strip()
        sb.append('='.join([key, '"%s"' % value.replace('"', '\\"')]))
    return ' '.join(sb)


def upload_monit_conf():
    "Uploads the monit conf for gunicorn."
    if not exists('/etc/monit/conf.d/'):
        puts('monit missing... skipping')
        return
    puts('Uploading monit config...')
    context = dict(
        projectpath='/www/yacs/django/',
        user=USER,
        gunicorn='/www/yacs/virtualenv/bin/gunicorn_django',
        workers=4,
        logs='/www/yacs/logs/',
        settings='yacs.settings',
        pid='/tmp/yacs.pid',
        env=remote_vars('YACS_DATABASE_URL', 'YACS_SECRET_KEY'),
    )
    upload_template('yacs.monit', '/etc/monit/conf.d/yacs.conf',
            context=context, use_sudo=True, backup=False)


def update_crontab():
    context = dict(
        projectpath='/www/yacs/django/',
        python='/www/yacs/virtualenv/bin/python',
        user=USER,
        logpath='/www/yacs/logs/',
    )
    upload_template('yacs.cron', 'yacs_cron', context=context, backup=False)
    sudo('crontab -u {0} yacs_cron'.format(USER))
    sudo('rm -f yacs_cron')


def managepy(command):
    sudo('%s manage.py %s' % (PYTHON, command), user=USER)


def validate_production_json():
    with open('yacs/settings/production.json', 'r') as handle:
        json.loads(handle.read())


@task
def deploy(upgrade=1):
    """Deploys to the given system.
    Use salt, chef, or puppet to configure the outside packages.

    Things required to be set up:
        - python
            - database driver
        - virtualenv
        - coffeescript
        - java
        - pip
        - database (postgres; postgres user)
            - created database & user
        - webserver (nginx; www-data user)
            - webserver config to proxypass to gunicorn (nginx)
        - memcached
    """
    #validate_production_json()
    upload_monit_conf()
    clean()
    with cd('/www/yacs/'):
        if not exists('virtualenv'):
            puts('Creating Virtual Environment...')
            sudo('virtualenv --distribute virtualenv', user=USER)
    puts('Uploading to remote...')
    with settings(warn_only=True):
        run('rm -rf tmp')
        run('mkdir tmp')
    upload_project(remote_dir='tmp')
    sudo('mv -f tmp/yacs /www/yacs/tmp')
    sudo('chown -R %s /www/yacs/tmp' % USER)
    sudo('chgrp -R %s /www/yacs/tmp' % GROUP)
    run('rm -rf tmp')
    with cd('/www/yacs/'):
        puts('Replacing remote codebase...')
        sudo('rm -rf django', user=USER)
        sudo('mv -f tmp django', user=USER)
    with cd('/www/yacs/django'):
        puts('Removing extra files...')
        with settings(warn_only=True):
            sudo('find . -name ".*" | xargs rm -r', user=USER)
            sudo('rm yacs.db', user=USER)
        puts('Installing dependencies...')
        prefix = '--upgrade'
        if not int(upgrade):
            prefix = ''
        sudo(PIP + ' install %s -r requirements/deployment.txt' % prefix, user=USER)
        sudo(PIP + ' install %s %s ' % (prefix, ADDITIONAL_PACKAGES), user=USER)
        puts('Running migrations...')
        managepy('syncdb --noinput')
        managepy('migrate --noinput')
        puts('Gathering static files...')
        managepy('collectstatic --noinput')
        puts("Clearing caches...")
        sudo('service memcached restart')
        managepy('clear_cache')
        puts('Restarting gunicorn...')
        sudo('service monit restart')
        sudo('monit restart yacs')
    update_crontab()
    puts('Done!')


@task
def fetch():
    "Tells the deployed system to fetch course data."
    with cd('/www/yacs/django'):
        puts('Getting course data from SIS...')
        sudo(PYTHON + ' manage.py import_course_data')
        puts('Fetching catalog data...')
        sudo(PYTHON + ' manage.py import_catalog_data')
        puts('Generating conflict cache...')
        sudo(PYTHON + ' manage.py create_section_cache')


@task
def clean():
    "Removes local python cache files."
    puts('Removing local object files and caches...')
    with settings(warn_only=True):
        local('find . -name "*.pyc" | xargs rm')
        local('find . -name "*.pyo" | xargs rm')
        local('find . -name "__pycache__" -type directory | xargs rm -r')
        local('rm -r yacs/static/root')


def wait_for_url(url, timeout=30):
    while timeout > 0:
        handle = None
        try:
            handle = urllib2.urlopen(url, timeout=timeout)
            handle.getcode()
            return
        except urllib2.URLError:
            time.sleep(1)
            timeout -= 1
        finally:
            if handle:
                handle.close()


@task
def jasmine(port=6856):
    local('jasmine-ci')


@task
def pep8():
    local('pep8 . --exclude=migrations --statistics --count --ignore=E501')


@task
def test():
    "Runs tests."
    clean()
    verbose()
    local('python manage.py test --failfast ' + ' '.join(APPS))
    pep8()
    local('python manage.py collectstatic --noinput')
    clean()


@task
def server(port=8000):
    local('python manage.py run_gunicorn -b "127.0.0.1:' + str(port) + '" -w 2')
