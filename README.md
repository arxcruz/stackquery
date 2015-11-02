# stackquery-dashboard
## Requirements
You need to have the following python packages in your system:
1. Flask
1. Flask-Restful
1. Flask-SQLAlchemy
1. simplejson
1. mechanize
1. odict

You can check the requirements.txt and install with pip:

    pip install -r requirements.txt


## Installation
### Using gunicorn
The installation is pretty straightforward, basically, you need to download the code from github, and change some settings in `websiteconfig.py` like for example the SQLAlchemy database:

    DATABASE_URI = 'mysql+mysqldb://user:password@localhost/stackquery'

And if you want to run in debug mode, just add this in your `websiteconfig.py`:
    DEBUG = True

After that, if you want to create the tables and populate the database, you can run the initdb.py script.
    python initdb.py --all

Use ```python initdb.py --help``` for more options.

Install gunicorn:

    sudo pip install gunicorn

or

    sudo dnf install python-gunicorn

and you can start the server with:

    gunicorn -w 4 stackquery:app

where ``-w`` is the number of workers that you want.
By default, gunicorn will run on port 8000. You can use Nginx to redirect to other port (80 for example)

#### Nginx conf file example
    server {
        listen 80;
        server_name example.com;
        access_log /var/log/nginx/stackquery.log;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host:80;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            #proxy_set_header Access-Control-Allow-Origin *;
        }
    }

You can add it in your Nginx config directory (on Fedora is `/etc/ngnix/conf.d`), restart the server and you're done.
