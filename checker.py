#!/usr/bin/env python

import config
import urllib.request
import json
import os

def main():
    resp = urllib.request.urlopen(config.api_url.format(config.token)).read().decode("utf-8")
    response = json.loads(resp)
    if response['ok'] == True:
        if response['result']:
            restart_server()
        else:
            restart_server()
    else:        
        restart_server()

def restart_server():
    os.system('pgrep -f telegram')

main()
