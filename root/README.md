xorg.conf dummy video display requires xserver-xorg-video-dummy package. located in /etc/X11/xorg.conf.d/
10-globally-managed-devices.conf located in /usr/lib/NetworkManager/conf.d/
wwan-vzwireless.nmconneciton located in /etc/NetworkManager/system-connections/


How to add *.nmconnection configuration for NetworkManager:
- sudo nmcli con add con-name wwan-vzwireless ifname cdc-wdm0 type gsm apn vzwinternet ipv4.method auto connection.autoconnect yes
- ^ If you do this line you do not need to input the *.nmconnection file as well, this command creates it and will adjust for your UUID.
- Good writeup: https://www.cbtechinc.com/wwan-lte-on-hpe-el300-with-linux-and-sierra-wireless-em7565/
