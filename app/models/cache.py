""" This file contains complete cache configuration.
"""
from flask_caching import Cache
from app import app


cache = Cache(config={'CACHE_TYPE': 'memcached',
                      'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_TIMEOUT'],
                      'CACHE_KEY_PREFIX': 'kipoi_website',
                      'CACHE_MEMCACHED_SERVERS': app.config['MEMCACHED_SERVERS'],
                      })