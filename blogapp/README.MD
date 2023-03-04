Pre-Requisites(for mac)
============
1. Create a virtualenv. Make sure to install a version of python 3.7.

		$ pip3 install virtualenv
		$ python3.7 -m venv env_name
2. Activate the virtualenv

		  $ source env_name/bin/activate
3. last But not least
       
		  $ pip install requirements.txt
4. Set Environment Variable For Run

		  $  export FLASK_APP=app.py
		  $  export FLASK_ENV=development
5. Make Migration File

		  $  flask db migrate -m "Initial migration."
		  $  export FLASK_ENV=development
6. Initialise Database

		  $   flask db init
7. Migrate DataBase

		  $  flask db upgrade
8. Run Server 

		  $  flask run