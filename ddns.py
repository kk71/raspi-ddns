#!/usr/bin/env python3
#coding=utf-8
'''
raspi watchdog


author:kK(fkfkbill@gmail.com)
'''


from dnspod import apicn
import ddnsconf
import sys
from urllib import request
from datetime import datetime



#====================================
def validation():
    '''
validate the configures
'''
    class domains_config_error(Exception):
        pass

    #domains
    domains=ddnsconf.domains
    if type(domains)!=list:raise domains_config_error("domains variable should be list")
    for account in domains:
        if type(account)!=dict:
            raise domains_config_error("every dnspod account should be a dict")
        if type(account["email"])!=str or\
           type(account["password"])!=str:
            raise domains_config_error("account email and password must be strs")
        if account["email"]=="" or\
           account["password"]=="":
            raise domains_config_error("account email or password shouldn't be empty.")
        if type(account["dns"])!=dict:
            raise domains_config_error("dns list should be dicts")
        for dns in account["dns"]:
            if type(dns)!=str:
                raise domains_config_error("domain name must be strs")
            for sub_domain in account["dns"][dns]:
                if type(sub_domain)!=str or sub_domain=="":
                    raise domains_config_error("sub domain must be strs")

    return True




#====================================
def sync_domains():
    '''
sync domains listed in config.py
'''
    for account in ddnsconf.domains:
        for domain_name in account["dns"]:
            try:#check if the domain exists
                domain_id=apicn.DomainId(domain_name,
                                         email=account["email"],
                                         password=account["password"])()["domains"]["id"]
            except:#domain not exist,then create it
                try:
                    domain_creation=apicn.DomainCreate(domain_name,
                                                       email=account["email"],
                                                       password=account["password"])()
                    domain_id=domain_creation["domain"]["id"]
                except:
                    print("domain named '%s' doesn't exist and is unable to create."%domain_name , 
                          file=sys.stderr)
                    continue
            try:#fetch record list for domain_name
                records=apicn.RecordList(domain_id=domain_id,
                                         email=account["email"],
                                         password=account["password"])()["records"]
            except:
                print("fetch record list for domain '%s' failed."%domain_name,
                      file=sys.stderr)
                continue
            record_list={}
            for per_record in records:
                if per_record["type"].lower()=="a":#only consider A name record
                    record_list.update({per_record["name"]:per_record["id"]})
            for sub_domain in account["dns"][domain_name]:
                if sub_domain not in record_list:#gonna create a record for it
                    try:
                        apicn.RecordCreate(sub_domain=sub_domain,
                                           record_type="A",
                                           record_line="默认".encode("utf-8"),
                                           value="1.1.1.1",
                                           ttl="600",
                                           mx=None,
                                           domain_id=domain_id,
                                           email=account["email"],
                                           password=account["password"])()
                    except:
                        print("fail to create new record '%s' for '%s'"%(sub_domain,domain_name),
                              file=sys.stderr)
                else:
                    try:
                        apicn.RecordDdns(record_id=record_list[sub_domain],
                                         sub_domain=sub_domain,
                                         record_line="默认".encode("utf-8"),
                                         record_type="A",
                                         domain_id=domain_id,
                                         ttl="600",
                                         email=account["email"],
                                         password=account["password"])()
                    except:
                        print("failed to refresh record '%s' at '%s'."%(sub_domain,domain_name),
                              file=sys.stderr)



#====================================
if __name__=="__main__":
    if validation():
        print("%s:config validation passed."%datetime.now())
        sync_domains()
        print("finished.")
