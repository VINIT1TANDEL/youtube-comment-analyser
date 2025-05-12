#!/bin/bash

# Update and install Chromium and Chromedriver
apt-get update
apt-get install -y chromium chromium-driver

# Start the Flask app
python Youtubecomment-analyser/app.py
