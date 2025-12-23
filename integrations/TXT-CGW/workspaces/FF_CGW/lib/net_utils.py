import os

def get_ip():
    try:
        addressPart = os.popen('ip addr show mlan0').read().split('inet ');
        fullAddr = addressPart[1];
        ipaddr = fullAddr.split("/")[0];
        print('IP-Addr : {}'.format(ipaddr));
        return ipaddr;
    except Exception as e:
        print('Error :', e);
        return '-1';


