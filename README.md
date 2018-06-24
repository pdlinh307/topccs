# Installation
## Database
Type: MySQL <br>
Database: **topccs** <br>
Import Command:
```bash
mysql -u <user> -p topccs < topccs.sql
```
## Python
### Install python
Version **3.6 or later**
```bash
sudo yum install python3.6
python3 --version
```
### Install pip
Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
```bash
sudo python3 get-pip.py
``` 
### Install required libs
```bash
cd /path/to/project
sudo pip3 install -r requirements.txt
```
# Configuration
## Supervisor
## Gunicorn
## Nginx
# API specs
|#      |URL    |Input  | Output    |
|:-------------|:-------------|:-------------|:-----|
|1    |   |   |   |