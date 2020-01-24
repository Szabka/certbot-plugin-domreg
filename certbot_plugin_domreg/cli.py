# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 09:34:32 2020
@author: szabka
"""
import sys

if sys.path[0] != '':
    sys.path.insert(0, '')
    
from certbot_plugin_domreg import domreg_api

import logging
import ssl
import requests
import xml.etree.ElementTree as ET
import urllib3
import time

urllib3.disable_warnings()
logger = logging.getLogger(__name__)

ns = {'html': 'http://www.w3.org/1999/xhtml'}


def domregcall(passwd):
    response = requests.post('https://domain.telekom.hu/uadmin/zone2.php', data={'zid':'','domain':'domain','pwd':passwd,'action':'L'}, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},verify=ssl.CERT_NONE)
    if response.ok:
       root = ET.fromstring(response.text)
       trr = root.findall(".//html:table[@class='zoneRecs']/html:tr",ns)
       for tr in trr:
           tdn = tr.findall("./html:td",ns)
           if tdn[2].text == 'IN TXT':
               print(tdn[4].find("./html:a",ns).get("onclick")[13:-9])
               print(tdn[0].text+':'+tdn[3].text)


if __name__ == '__main__':
#    domregcall('***')
     print(domreg_api.add_txt_record('***','domain', '_acme-challenge.domain', 'challenge'))
     time.sleep(10)
     print(domreg_api.del_txt_record('***','domain', '_acme-challenge.domain', 'challenge'))

