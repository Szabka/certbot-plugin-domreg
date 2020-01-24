import ssl
import requests
import xml.etree.ElementTree as ET
import urllib3
import dns.resolver
import re
import time

from certbot.plugins import dns_common

urllib3.disable_warnings()

ns = {'html': 'http://www.w3.org/1999/xhtml'}

def _request(passwd,zid,domain,action):
    return requests.post(url='https://domain.telekom.hu/uadmin/zone2.php', headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data={'zid':zid,'domain':domain,'pwd':passwd,'action':action},verify=ssl.CERT_NONE)

#find manageable domain part in domreg
def _get_base_domain(passwd,domain):
    for candidate_base_domain in dns_common.base_domain_name_guesses(domain):
        response = _request(passwd,'',candidate_base_domain,'L')
        if response.ok:
            try:
                root = ET.fromstring(response.text)
                trr = root.findall(".//html:table[@class='zoneRecs']/html:tr",ns)
                if trr:
                    return candidate_base_domain
            except ET.ParseError:
                print(candidate_base_domain+' is not base.')
    return None


def _get_relative_name(base_domain, name):
    suffix = '.' + base_domain
    return name[:-len(suffix)] if name.endswith(suffix) else None

# return the zid for the existing TXT record
def _get_txt_record(passwd,base_domain, relative_name, value):
    response = _request(passwd,'',base_domain,'L')
    if not response.ok:
        return None
    root = ET.fromstring(response.text)
    trr = root.findall(".//html:table[@class='zoneRecs']/html:tr",ns)
    for tr in trr:
        tdn = tr.findall("./html:td",ns)
        if tdn[2].text == 'IN TXT' and tdn[0].text == relative_name and value == tdn[3].text:
            return tdn[4].find("./html:a",ns).get("onclick")[13:-9]

    return None


def _update_record(passwd,domain, name, value, add=True):
#    print(passwd+';'+domain+';'+name+';'+value+';'+str(add))
    base_domain = _get_base_domain(passwd,domain)
    if base_domain is None:
        return 'Unable to get base domain for "{}"'.format(domain)
    relative_name = _get_relative_name(base_domain, name)
    if relative_name is None:
        return 'Unable to derive relative name for "{}"'.format(name)

#    print(base_domain+";"+relative_name);
    zid =_get_txt_record(passwd,base_domain,relative_name,value)
    if add:
        if zid==None: 
            serial = _get_domain_serial(base_domain)
            response = requests.post(url='https://domain.telekom.hu/uadmin/zone2.php', headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data={'host':relative_name,'ttl':'300','type':'TXT','data2':'','data1':value,'domain':base_domain,'pwd':passwd,'action':'A'},verify=ssl.CERT_NONE)
            if response.ok and serial!=None:
                print('waiting for serial change, current: '+serial)
                maxchecks = 61
                while (_get_domain_serial(base_domain)==serial and maxchecks>0):
                    time.sleep(60)
                    maxchecks=maxchecks-1
        else:
            print("record already exist with zid: "+zid)
            return None
    else:
        if zid!=None:        
            response = _request(passwd,zid,base_domain,'D')
        else: 
            print("record not found, nothing to delete")
            return None
    return None if response.ok else 'Error'

def _get_domain_serial(domain):
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['195.228.240.85','195.56.77.76']
    response = dns.resolver.query(domain, 'SOA')

    if response.rrset is not None:
        pattern= r'(%s)\.\s(\d{1,})\s(\w+)\sSOA\s(.*?)\.\s(.*?)\.\s(\d{1,})\s(\d{1,})\s(\d{1,})\s(\d{1,})\s(\d{1,})' % domain
        match = re.match(pattern, str(response.rrset))
        m_name, ttl, class_, ns, email, serial, refresh, retry, expiry, minim = match.groups()
        return serial
    return None
   
    
#external interface
def add_txt_record(passwd,domain, name, value):
    return _update_record(passwd,domain, name, value,True)

#external interface
def del_txt_record(passwd,domain, name, value):
    return _update_record(passwd,domain, name, value,False)

