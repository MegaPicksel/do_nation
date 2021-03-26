# Do Nation

Do Nation allows users to pledge towards taking action to have a positive effect on the environment.
This application stores and displays data for users, pledges, and the actions that they pledge towards.

## Installation and setup
This project uses the Django framework, for more info please visit: https://docs.djangoproject.com/en/3.1/

First create a venv using Python3:

```console
python3 -m venv venv
```

Activate the venv:

```console
source venv/bin/activate
```

Install dependencies:

```console
cd do_nation/
pip install -r requirements.txt
```

Setup the database:

```console
python manage.py makemigrations
python manage.py migrate
```

To create a super user run this command and follow the on screen prompts:

```console
python manage.py createsuperuser
```

## Run the tests

The tests use pytest, firs the settings module to use must be set as an environment variable:

```console
export DJANGO_SETTINGS_MODULE=do_nation.settings
```

The the tests can be run:

```console
pytest pledges/tests
```

## Start the server

To start the server:

```console
python manage.py runserver
```

Go to `http://127.0.0.1:8000` to view the project.
Go to `http://127.0.0.1:8000/admin` to add data to the database.