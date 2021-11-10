# website

[![CircleCI](https://circleci.com/gh/kipoi/website.svg?style=svg&circle-token=c240f6a27d9bf721d28111e83d28a193c450757e)](https://circleci.com/gh/kipoi/website)

Kipoi website hosted at <http://kipoi.org>.

## Usage

```
$ make
Please use `make <target>' where <target> is one of
  freeze        to generate a static webpage
  serve         Serve the flask app
  serve-freeze  Serve frozen flask app.
  clean         clean the generated files

$ make serve
````

## Pre-requirements

### Virtual python environment with python 3.9

Create a conda (or as per your choice) virtual environment using python 3.9. It is also possible to use python version >=3.6<=3.8

```bash
conda create -n websiteenv python=3.9
```

### Kipoi

Install Kipoi package by following installation process from [here](https://github.com/kipoi/kipoi) and kipoiseq from [here](https://github.com/kipoi/kipoiseq). It is also required to install kipoi-veff2. Please follow the following steps inside your conda environment

```
pip install cyvcf2 (Use conda if using python=3.6)
pip install dataclasses (only for python=3.6)
pip install git+https:/github.com/kipoi/kipoi-veff2
```


## Requirements

All python requirements are listed in `app/requirements.txt` file.

Installation of python requirements:

```bash
pip3 install -r app/requirements.txt
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
