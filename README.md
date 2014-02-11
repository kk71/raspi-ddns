Raspi-ddns
===============

raspberry pi ddns(dynamic dns)

## Environment
* python3.3+
* bash
* systemd(for service support)
* netctl(for network, optional)


## Usage alongside systemd

clone git repo in root home dir so that it\'ll be reachable for systemd to start it as a daemon. 
Note if you'd like to put elsewhere(but must be under a root folder),change the script pathname in raspi-ddns.service otherwise bash won't find it.
then run:
```bash
    #in root user
    cd
    git clone https://github.com/kk71/raspi-ddns.git
```

for systemd service installation, after that,run
```bash
    #in root user
    ./raspi-ddns.sh install-service [time interval] [interface]
```

note:
* time interval defined the ddns interval
* interface is the network interface to access the Internet directly, 
it must has it's standalone IP in public Internet. 
If you ignored it, then network availibility check is ignored too.

to disable and stop rasp-ddns immediately,use:
```bash
    #in root user
    ./raspi-ddns.sh delete-service
```
