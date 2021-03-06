# YACS [![Build Status](https://secure.travis-ci.org/jeffh/YACS.png?branch=master)](http://travis-ci.org/jeffh/YACS)
Simple, Sane Course Scheduling.

YACS is a web-based course schedule with an emphasis on usability.
It is also flexible enough to work with other school course data.

Send questions and comments to [@jeffhui][] or jeffh@alumni.rpi.edu.

If you're an RPI student and looking to use it, go to [yacs.me][yacsme]

[@jeffhui]: http://twitter.com/jeffhui "Twitter: @jeffhui"
[yacsme]: http://yacs.me/ "YACS - The usable online course scheduler"

## Setup
YACS is actively developed on [Python][] 2.7. So go get that installed first.
It's good python practice to put this project inside a [virtualenv][],
but that's beyond the scope of this README.

You can download an archive from the top-right of the github page or clone the repo:

    git clone git://github.com/jeffh/YACS.git

Which will download code into a YACS folder where you run this command.

[Python]: http://python.org/
[virtualenv]: http://www.virtualenv.org/en/latest/index.html

### Dependencies

YACS is built on top of [Django][] 1.5. Thus, it requires a database driver to run.
Install the appropriate driver and its database, or just use the bundled SQLite.

[Django]: https://www.djangoproject.com/ "Django Web Framework"

### Setup (Development)

1. YACS uses a lot of dependencies. It relies on [pip][] to install most of them. Simply do:
    `pip install -r requirements/development.txt`
   Which will install all the dependencies YACS needs (minus the database driver).


2. Edit `DATABASES` variable in the `yacs/settings/development.py` file to your
   appropriate database settings.

3. Run the following commands. When calling syncdb, you'll be ask to create a superuser,
   it is purely optional, only the debug-toolbar is visible for logged in super-users.

    ```
    python manage.py syncdb
    python manage.py migrate
    ```

4. Next we need to get some data. Run these commands to import and setup the data for use.
   (These will take awhile).

    ```
    python manage.py import_course_data   # imports from RPI SIS
    python manage.py import_catalog_data  # imports from RPI course catalog
    python manage.py create_section_cache # creates cache for generating schedules
    ```

5. Check it out by running the dev server `python manage.py runserver` and pointing your
   browser to [http://localhost:8000/][local] and viola!

6. YACS uses [coffeescript][] as its basis for javascript. So if you want to modify the
   javascript code, you'll need to have the coffeescript compiler installed.

7. (Optional) If you plan on editing the CSS. YACS uses [SASS][] to generate the CSS.
   Once you installed it, use `make scss` to make sass automatically update the
   stylesheets as you change them.

8. ???
9. Profit?

[coffeescript]: http://coffeescript.org/
[SASS]: http://sass-lang.com/
[pip]: http://www.pip-installer.org/en/latest/index.html
[local]: http://localhost:8000/

## Setup (Production)

It's probably best to use the associated project: [seafood][]. Which is a [salt][]
configuration project that can be used to set up a server for YACS.

The following environmental variables are used in production:

- **YACS_DATABASE_URL**: The database url to connect. Parsed using dj_database_url.
                         In the form of dbengine://user:pass@host/dbname
- **YACS_SECRET_KEY**: The internal django secret key to use. Be unique!
- **YACS_EMAIL_FROM**: The email address the sender comes from
- **YACS_EMAIL_USE_TLS**: The smtp server requires TLS (yes, no), defaults to yes.
- **YACS_EMAIL_HOST**: The smtp server to connect to
- **YACS_EMAIL_USER**: The smtp username
- **YACS_EMAIL_PASS**: The smtp password
- **YACS_EMAIL_PORT**: The smtp server port, defaults to 587

When using [seafood][], you'll need to modify the salt configuration files to be
unique for your installation. YACS uses email for notifying ADMINS in project settings.

After using [seafood][] to set up the environment, use:

    ```
    fab -H root@my-server deploy
    ```

To deploy YACS to the server. Updates can be deployed to the server in the same fashion.

[seafood]: https://github.com/jeffh/seafood
[salt]: http://saltstack.org

## Project layout
Currently the project is laid out as follows:

- **api**: API application. Where all  API related code is. Relies on courses and scheduler app.
- **courses**: The courses application. Contains the schema and manages the storage of course data. Also contains course-data-displaying views.
- **courses_viz**: An application that stores visualization of course data. (Part of Introduction to Visualization class)
- **jslog**: An application that can record basic JS data for debugging.
- **lib**: Contains library code that can, be potentially, separated into an independent project. To enforce this separability, this folder is added to the sys.path for absolute imports
- **scheduler**: This app handles course scheduling. Relies on the courses app for all the course data.
- **yacs**: Project files. Contains settings, root urls, templates, static files, etc.
- **test_reports**: Only appears when tests are executed. Used to see the test coverage.
- **requirements**: Contains various requirement files for PIP.
- **Makefile**: Used for running tests, cleaning python caches and deployment.
- **manage.py**: Django's CLI.

## Help
This project is still evolving. There are still issues to tackle. Go to the [GitHub issues][issues] page to see them all.

[issues]: https://github.com/jeffh/YACS/issues
