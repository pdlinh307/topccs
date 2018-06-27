# Overview
This project was developed by [Realtel Vietnam](https://realtel.vn).
```text
Version: 1.0
Release date: 27/06/2018
```

# Administrator's guide
A step by step guide for system administrators or anyone else who might deploy this project.
## Requirements
* *CentOS 7*
* *MySQL 5.7 or later*
* *Python 3.6.x*
* *Asterisk 13*

## Setting up environments
### OS
```bash
sudo yum -y install epel-release
sudo yum -y update
```
### Database 
#### Install mysql server (if not exists)
```bash
sudo yum -y install mysql-server
mysql_secure_installation
```
#### Create database and user 
Replace `db_name`, `hostname` and `p4ssw0rd` with your username, hostname and password respectively. 
```sql
CREATE DATABASE IF NOT EXISTS `topccs` DEFAULT CHARACTER SET utf8;
CREATE USER 'db_user'@'hostname' IDENTIFIED BY 'p4ssw0rd';
GRANT ALL ON topccs.* TO 'db_user'@'hostname';
FLUSH PRIVILEGES;
```
#### Import
Replace `db_user` with username that created above.
```bash
mysql -u db_user -p topccs < topccs.sql
```
### Python
#### Install python
```bash
sudo yum install python3.6
sudo rm -f /usr/bin/python3
sudo ln -s /usr/bin/python3.6 /usr/bin/python3
python3 --version
```
#### Install pip
Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py).
```bash
sudo python3 get-pip.py
``` 
#### Install required libs
Download project.
```bash
cd /path/to/project
sudo pip3 install -r requirements.txt
```
#### Install supervisor
```bash
sudo pip install supervisor
sudo mkdir /etc/supervisor
sudo mkdir /etc/supervisor/conf.d
sudo mkdir /var/log/supervisor
sudo echo_supervisord_conf > /etc/supervisor/supervisord.conf
```

## Configurations
### Supervisor
#### API web services
`updating ...`
#### Celery tasks
`updating ...`
### Gunicorn
`updating ...`
### Nginx (optional)
`updating ...`

## Service
`updating ...`

# API docs
The technical reference to CRM developer.

`updating ...`

|#      |URL    |Input  | Output    |
|:-------------|:-------------|:-------------|:-----|
|1    |   |   |   |