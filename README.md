Cabot Pushover Plugin
=====

This is an alert plugin for the cabot service monitoring tool. It allows you to alert users by their user key.

## Installation

Install using pip

    pip install .

Edit `conf/production.env` in your Cabot clone to include the plugin:

    CABOT_PLUGINS_ENABLED=cabot_alert_pushover...,<other plugins>

## Configuration

The plugin requires the following environment variable to be set:

    PUSHOVER_APIKEY=<app_api_key>
