"""
Project applications.

Every Django app written for this project lives here as ``apps.<name>`` and is
registered in ``LOCAL_APPS`` (``config/settings/base.py``). Create a new one with:

    python manage.py startapp myapp apps/myapp

then set ``name = "apps.myapp"`` on its ``AppConfig``; ``startapp`` writes the
bare app name, which Django cannot import from this package.
"""
