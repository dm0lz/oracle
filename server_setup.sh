#!/bin/bash

sudo apt install -y htop
sudo apt install -y python3-pip
sudo apt install -y unzip

if [ -f /swapfile ]; then
  echo "The swap file /swapfile exists."
else
  echo "The swap file /swapfile does not exist."
  sudo fallocate -l 24G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi