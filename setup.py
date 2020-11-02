#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '1.0.0'

setup(name='cabot-alert-pushover',
      version=VERSION,
      description='A Pushover alert plugin for Cabot',
      author='MattZK',
      author_email='matthias@districtthree.be',
      url='http://cabotapp.com',
      packages=find_packages(),
      download_url='https://github.com/mattzk/cabot-alert-pushover/archive/{}.zip'.format(VERSION),
     )
