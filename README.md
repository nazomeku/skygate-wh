# skygate-wh

Recruitment [task](https://github.com/nazomeku/skygate-wh/blob/master/task.txt) for internship in [Skygate](https://skygate.io/) with [live demo](http://nazo.pm/wh).


## Application for warehouse management

### Features:
- manage shelf content (update, remove)
- manage product (create, update, remove)
- manage transport (update, remove, suspend)
- transfer from shelf to transport
- sort to optymalize transport flow

### Updates:
- some validations (random fill with consideration of product quantity in warehouse)
- code cleaning (separated services file with functions)
- better sort (proper rotation messages)

### TBD:
- proper tests

### Technologies used:
- Python 3.6
- Gunicorn
- Flask
- Nginx
- SQLAlchemy
- Bootstrap 4


## Local deployment

1. Install dependencies.
```sh
$ pip install -r requirements.txt
```

2. Initlize database.
```sh
$ python
>>> from app import db
>>> db.create_all()
>>> exit()
$ python run.py
```


## Remote deployment (Ubuntu 16.04 LTS)

1. Clone repository
```sh
$ git clone https://github.com/nazomeku/skygate-wh.git
```
2. Rename directory and file name.
```sh
$ mv skygate-wh skygate && cd skygate && mv run.py wsgi.py
```
3. Create virtual enviroment.
```sh
$ virtualenv skygate
```
3. Activate virtual enviroment.
```sh
$ source skygate/bin/activate
```
4. Install requirements under your virtual enviroment.
```sh
(skygate) $ pip install -r requirements.txt
```
5. Initlize database.
```sh
$ python
>>> from app import db
>>> db.create_all()
>>> exit()
```
6. Test if application works (remember to allow port 5000 on firewall).
```sh
(skygate) $ gunicorn --bind 0.0.0.0:5000 wsgi:app
```
7. Deactivate virtual enviroment.
```sh
$ deactivate
```
8. Create service file (remember to change your username).
```sh
$ sudo nano /etc/systemd/system/skygate.service
```
```sh
[Unit]
Description=Gunicorn instance to serve skygate app
After=network.target

[Service]
User=username
Group=www-data
WorkingDirectory=/home/username/skygate
Environment="PATH=/home/username/skygate/skygate/bin"
ExecStart=/home/username/skygate/skygate/bin/gunicorn --workers 3 --bind unix:skygate.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
9. Start application.
```sh
$ sudo systemctl start skygate
```
10. Enable application to start at boot.
```sh
$ sudo systemctl enable skygate
```
11. Configure your domain.
```sh
$ sudo nano /etc/nginx/sites-available/skygate
```
12. Enable your site.
```sh
$ sudo ln -s /etc/nginx/sites-available/skygate /etc/nginx/sites-enabled
```
13. Check if there is no error with nginx config.
```sh
$ sudo nginx -t
```
14. Restart nginx.
```sh
$ sudo systemctl restart nginx
```
