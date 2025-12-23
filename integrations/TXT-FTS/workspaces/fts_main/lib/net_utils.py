import os

def get_ip():
    ip_prefix = '192.168.0'
    try:
        with os.popen('ip addr show') as f:
            output = f.readlines()
            # Iterate through the lines to find the IP address with the given prefix
            for line in output:
                line = line.strip()
                if line.startswith('inet') and ip_prefix in line:
                    parts = line.split(" ")
                    for part in parts:
                        if part.startswith(ip_prefix):
                            # Split by slash to remove the subnet mask
                            ip_address = part.split('/')[0]
                            print('IP-Addr : {}'.format(ip_address));
                            return ip_address
        return -1
    except Exception as e:
        print('Error :', e);
        return '-1';


