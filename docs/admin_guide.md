# Administrator's guide
A step by step guide for system administrators or anyone else who might deploy this project.

If you are CRM developer, please read [this document](docs/api_spec.md).

## Requirements
* *CentOS 7*
* *MySQL 8.0 (recommended) or MariaDB (10.3)*
* *Python >= 3.5 (3.6.x recommended)*
* *Redis >= 3.0*
* *Asterisk 13*

## Setting up environments
### Database 
#### Create database and user 
Replace `db_name`, `hostname` and `p4ssw0rd` with your username, hostname and password respectively. 
```sql
CREATE DATABASE IF NOT EXISTS `topccs` DEFAULT CHARACTER SET utf8;
CREATE USER 'db_user'@'hostname' IDENTIFIED BY 'p4ssw0rd';
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
### Project's config
- **config/mysql.conf**

```ini
[client]
host=<hostname_or_ipaddress>
port=3306
user=<username_for_mysql>
password=<password_for_username>
database=topccs
autocommit=True
```

- **config/campaign.conf**

```ini
[ami]
host        = <hostname_or_ipaddress>
port        = 5038
user        = <username>
secret      = <secret_for_username>
encoding    = utf8

[trunk]
context     = SIP/mkt
queue       = 8000
timeout     = 30

[scheduler]
retry       = 3
interval    = 3600
rate_limit  = 2m

[api]
datetime_format     = %%Y-%%m-%%d %%H:%%M:%%S
cp_required_fields  = campaignid,typeid,contact,code,starttime,endtime
cts_required_field  = phonenumber

[callback]
finish_campaign = http://crm.native.vn/api/FinishCampaign
update_campaign = http://crm.native.vn/api/UpdateCampaign
timeout         = 3
```

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
