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
touch /etc/init.d/node_exporter

sudo echo "
#!/bin/bash
#
# chkconfig: 2345 90 12
# description: node-exporter server
#

# Get function from functions library
. /etc/init.d/functions

# Start the service node-exporter
start() {
        echo -n 'Starting node-exporter service: '
        nohup /usr/local/bin/node_exporter &
        ### Create the lock file ###
        touch /var/lock/subsys/node_exporter
        success $'node_exporter service startup'
        echo
}

# Restart the service node-exporter
stop() {
        echo -n 'Shutting down node-exporter service: '
        killproc node_exporter
        ### Now, delete the lock file ###
        rm -f /var/lock/subsys/node_exporter
        echo
}

### main logic ###
case '$1' in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status node_exporter
        ;;
  restart|reload)
        stop
        start
        ;;
  *)
        echo $'Usage: $0 {start|stop|restart|reload|status}'
        exit 1
esac

exit 0
" > /etc/init.d/node_exporter

# Start node_exporter service. It will listen on port 9100
sudo service node_exporter start