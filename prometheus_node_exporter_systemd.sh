#!/bin/bash
# Exit if it is already installed
if [[ -f /usr/local/bin/node_exporter ]]; then
  exit 0
fi

# Get the JSON for download the latest Linux AMD64 binary
BDU2="{$(curl -s https://api.github.com/repos/prometheus/node_exporter/releases/latest | grep "browser_download_url" | grep "linux-amd64.tar.gz")}"

# Extract the download url from the JSON - Not ideal, we should be using jq or other parser but I wanted to use only default tools.
DURL2=$(echo $BDU2 |  awk -F'"' '{print $4}')

# Download, extract and move the binary to /usr/local/bin
wget $DURL2
tar xvfz node_exporter-*.*-amd64.tar.gz
mv node_exporter-*.*-amd64/node_exporter /usr/local/bin/

# Create user to run node_exporter
useradd -rs /bin/false node_exporter

# Create systemd unit server file and fill it
touch /etc/systemd/system/node_exporter.service

echo "
[Unit]
Description=Node Exporter
After=network.target
[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/node_exporter.service

# Reload systemd then enable (for startup on boot) and start node_exporter service. It will listen on port 9100
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter