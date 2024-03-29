Tables of contents:
- [Administrator's guide](#administrators-guide)
    - [Requirements](#requirements)
    - [Setting up environments](#setting-up-environments)
        - [Database](#database)
            - [Create database and user](#create-database-and-user)
            - [Import](#import)
        - [Python](#python)
            - [Install pip](#install-pip)
            - [Install required libs](#install-required-libs)
            - [Install supervisor](#install-supervisor)
    - [Configurations](#configurations)
        - [Project's config](#projects-config)
            - [MySQL](#mysql)
            - [Project](#project)
        - [Supervisor](#supervisor)
            - [Supervisord](#supervisord)
            - [Worker](#worker)
            - [API](#api)
            - [Event Listener](#event-listener)
        - [Asterisk](#asterisk)
        - [Nginx (optional)](#nginx-optional)
    - [Control processes](#control-processes)

# Administrator's guide

A step by step guide for system administrators or anyone else who might deploy this project.

If you are CRM developer, please read [this document](apispecs.md).

## Requirements

* *CentOS 7*
* *MySQL 8.0 (recommended) or MariaDB (10.3)*
* *Python >= 3.5 (3.6.x recommended)*
* *Redis >= 3.2*
* *Asterisk 13*
* *Nginx (optional)*

## Setting up environments

### Database

#### Create database and user

Replace `db_name`, `hostname` and `db_password` with your username, hostname and password respectively.

```sql
CREATE DATABASE IF NOT EXISTS `topccs` DEFAULT CHARACTER SET utf8;
CREATE USER 'db_user'@'hostname' IDENTIFIED BY 'db_password';
GRANT ALL ON topccs.* TO 'db_user'@'hostname';
FLUSH PRIVILEGES;
```

#### Import

Replace `db_user` with username that created in previous step.

```bash
mysql -u db_user -p topccs < topccs.sql
```

### Python

#### Install pip

Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py).

```bash
sudo python3.6 get-pip.py
``` 

#### Install required libs

Download project.

```bash
cd /path/to/project
sudo pip3.6 install -r requirements.txt
```

#### Install supervisor

Replace `nonroot` with normal user.

```bash
sudo pip install supervisor
sudo mkdir /etc/supervisor
sudo mkdir /etc/supervisor/conf.d
sudo mkdir /var/log/supervisor
sudo chown -R nonroot:nonroot /etc/supervisor
sudo chown -R nonroot:nonroot /var/log/supervisor
sudo echo_supervisord_conf > /etc/supervisor/supervisord.conf
```

## Configurations

### Project's config

#### MySQL

config/mysql.conf

```ini
[client]
host        = <mysql_server>
port        = 3306
user        = <db_user>
password    = <db_password>
database    = topccs
autocommit  = True
```

#### Project

config/app.conf

```ini
[ami]
host            = <voip_server>
port            = 5038
user            = <ami_user>
secret          = <ami_secret>
encoding        = utf-8

[originate]
trunk       = SIP/mkt
context     = from-internal
queue       = 8000
timeout     = 30000
priority    = 1
record_url  = http://42.116.18.42:8000/recordings/

[scheduler]
retries     = 3
interval    = 3600
rate_limit  = 2/m

[api]
datetime_format             = %%Y-%%m-%%d %%H:%%M:%%S
required_fields_campaign    = campaignid,contact,starttime,endtime
required_field_contacts     = phonenumber

[callback]
finish_campaign = http://crm.native.vn/api/FinishCampaign
update_campaign = http://crm.native.vn/api/UpdateCampaign
timeout         = 3

[redis]
host            = localhost
port            = 6379
worker_db       = 1
scheduler_db    = 2
```

### Supervisor

#### Supervisord

/etc/supervisor/supervisord.conf

```ini
# change 2 last rows
[include]
files = conf.d/*.ini
```

#### Worker

/etc/supervisor/conf.d/topccs-wk.ini

```ini
[program:topccs-wk]
command         = /usr/bin/celery -A cworker worker -E -l INFO --autoscale=8,4
directory       = /home/dev/topccs
autostart       = true
autorestart     = true
startretries    = 5
stdout_logfile  = /var/log/supervisor/topccs-wk.out.log
stderr_logfile  = /var/log/supervisor/topccs-wk.err.log
```

#### API

/etc/supervisor/conf.d/topccs-api.ini

```ini
[program:topccs-api]
command         = /usr/bin/gunicorn -w 9 -b 127.0.0.1:3007 apis:app --access-logfile - --max-requests 5000 --max-requests-jitter 10
directory       = /home/dev/topccs
autostart       = true
autorestart     = true
startretries    = 5
stdout_logfile  = /var/log/supervisor/topccs-api.out.log
stderr_logfile  = /var/log/supervisor/topccs-api.err.log
```

#### Event Listener

/etc/supervisor/conf.d/topccs-el.ini

```ini
[program:topccs-el]
command         = /usr/bin/python3.6 event_listener.py
directory       = /home/dev/topccs
autostart       = true
autorestart     = true
startretries    = 5
stdout_logfile  = /var/log/supervisor/topccs-el.out.log
stderr_logfile  = /var/log/supervisor/topccs-el.err.log
```

### Asterisk

/etc/asterisk/asterisk.conf

```ini
[options]
systemname  = topinative
```

/etc/asterisk/cdr_manager.conf

```ini
[general]
enabled         = yes

[mappings]
linkedid        => Linkedid
did             => Did
recordingfile   => RecordingFile
```

/etc/asterisk/manager.conf

```ini
[general]
enabled             = yes
timestampevents     = yes
allowmultiplelogin  = yes
```

/etc/asterisk/manager_custom.conf

```ini
[<ami_user>]
secret          = <ami_secret>
deny            = 0.0.0.0/0.0.0.0
permit          = 127.0.0.1/255.255.255.255
read            = all
write           = all
writetimeout    = 5000
displayconnects = yes
```

### Nginx (optional)

```text
server {
    listen 80;

    server_name _;

    access_log  /var/log/nginx/topccs.access.log;
    error_log  /var/log/nginx/topccs.error.log;

    location /api {
        proxy_pass         http://127.0.0.1:3007;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }
}
```

## Control processes

Commands run by normal user to control supevisor processes

```bash
# Start supervisor
supervisord -c /etc/supervisor/supervisord.conf
# (Show status|Stop|Start|Restart) (all|<program_name>)
supervisorctl show|stop|start|restart all|program_name
# For example: restart program which named is topccs-wk
supervisorctl restart topccs-wk
# Reload after re-config
supervisorctl reread
supervisorctl reload
```
