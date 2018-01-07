# website

Kipoi website

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

Installation of requirements:

```bash
pip3 install -r requirements.txt
```

## Deployment

Development web server can be run by executing following command from within the `app` folder, but for production purposes a Dockerfile is supplied. For development purposes, webserver is listening on the port 5000.

```bash
python main.py
```

### Docker

Base docker image can be seen [here](https://github.com/tiangolo/uwsgi-nginx-flask-docker).

Build docker image:

```bash
docker build -t kipoi-webapp .
```

Run a container based on your image:

```bash
docker run -d --name kipoi -p 80:80 kipoi-webapp
```
