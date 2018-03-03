# website

Kipoi website hosted at <http://kipoi.org>.

## Pre-requirements

### Kipoi

Install Kipoi package by following installation process from [official repository](https://github.com/kipoi/kipoi).

### git-lfs

Easiest way to install `git-lfs` is by adding git-lfs to the apt list following [this](https://packagecloud.io/github/git-lfs/install) tutorial.

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt install git-lfs
```

## Requirements

All python requirements are listed in `requirements.txt` file.

Installation of python requirements:

```bash
pip3 install -r requirements.txt
```

To speed-up operations like `kipoi.get_source("kipoi").list_models` or `kipoi.get_source("kipoi").list_models_by_group()` that internally trigger `git pull` on kipoi project, we use __memcached__ service to cache results for the duration set in `config.py` under `CACHE_DURATION` entry.

To enable cache it is enough to install and run `memcached` service locally. App by default expects memcached service on `127.0.0.1:11211`. If memcached service is deployed elsewhere, the `MEMCACHED_SERVERS` config entry inside `config.py` should be updated accordingly.

```bash
# Install memcached
sudo apt install memcached
```

When installing memcached on Ubuntu, service comes preconfigured to run at boot, unlike on CentOS7. To enable run at boot, issue the following commands:

```bash
# Enable run at boot
systemctl start memcached
systemctl enable memcached
systemctl status memcached
```

## Deployment

Development web server can be run by executing following command from within the `app` folder, but for production purposes a Dockerfile is supplied. For development purposes, webserver is listening on the port 5000.

```bash
python run.py
```

### Docker

Docker deployment is currently not supported due to the difficulties with git permissions.

Base docker image can be seen [here](https://github.com/tiangolo/uwsgi-nginx-flask-docker).

Build docker image:

```bash
docker build -t kipoi-webapp .
```

Run a container based on your image:

```bash
docker run -d --name kipoi -p 80:80 kipoi-webapp
```

### Static webpage

Run

```bash
make freeze
```

This will generate a static webpage located under `app/build`. If you wish to serve that directory, run

```bash
make serve-freeze
```

This will start python's simple http server from directory `app/build` on port 8000.
