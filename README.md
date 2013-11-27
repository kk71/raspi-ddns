Raspi-ddns
===============

raspberry pi ddns(dynamic dns)

## environment
* python3.3+
* curl
* bash
* systemd(for service support)
* network manager(for network,optional)


## usage alongside systemd

clone git repo in root home dir so that it\'ll be reachable for systemd to start it as a daemon. Note if you'd like to put elsewhere(but must be under a root folder),change the script pathname in raspi-ddns.service otherwise bash won't find it.
then run:
```bash
    # cd /root
    # git clone https://github.com/kk71/raspi-ddns.git
```

for systemd service installation,after that,run
```bash
    # cp raspi-ddns/ddns.service /etc/systemd/system/ddns.service 
    # systemctl enable ddns
```
to enable ddns as a service at the startup of the raspberry pi.

to start/stop rasp-ddns immediately,use:
```bash
    # systemctl start ddns
    # systemctl stop ddns
```

for normal usage without systemd,
```bash
    # ./raspi-ddns.sh
```
and all logs are in ddns.log
