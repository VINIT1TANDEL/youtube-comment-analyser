#!/bin/bash

# Update system packages
apt-get update

# Install Chromium and Chromedriver dependencies
apt-get install -y wget unzip curl gnupg

# Add Google's Debian repo (needed for Chromium)
curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list
apt-get update

# Install Chrome (not chromium-browser; we need the full one)
apt-get install -y google-chrome-stable

# Install ChromeDriver matching Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1 | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q -O /tmp/chromedriver.zip \
  "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Start the Flask app


python Youtubecomment-analyser/app.py
