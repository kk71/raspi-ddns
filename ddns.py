#!/usr/bin/env python3
# coding=utf-8
'''
raspi watchdog
author:kK(fkfkbill@gmail.com)

usage:
./ddns.py         :normally startup
'''

from dnspod import apicn
import ddnsconf
import logging


def validation():
    '''
validate the configures
'''
    class domains_config_error(Exception):
        pass

    # domains
    domains = ddnsconf.domains
    if not isinstance(domains, list):
        raise domains_config_error("domains variable should be list")
    for account in domains:
        if not isinstance(account, dict):
            raise domains_config_error("every dnspod account should be a dict")
        if not isinstance(account["email"], str) or\
           not isinstance(account["password"], str):
            raise domains_config_error(
                "account email and password must be strs")
        if account["email"] == "" or\
           account["password"] == "":
            raise domains_config_error(
                "account email or password shouldn't be empty.")
        if not isinstance(account["dns"], dict):
            raise domains_config_error("dns list should be dicts")
        for dns in account["dns"]:
            if not isinstance(dns, str):
                raise domains_config_error("domain name must be strs")
            for sub_domain in account["dns"][dns]:
                if not isinstance(sub_domain, str) or sub_domain == "":
                    raise domains_config_error("sub domain must be strs")
    return True


def sync_domains():
    '''
sync domains listed in config.py
'''
    for account in ddnsconf.domains:
        for domain_name in account["dns"]:
            try:  # check if the domain exists
                domain_id = apicn.DomainId(domain_name,
                                           email=account["email"],
                                           password=account["password"])()["domains"]["id"]
            except:  # domain not exist,then create it
                try:
                    domain_creation = apicn.DomainCreate(domain_name,
                                                         email=account[
                                                             "email"],
                                                         password=account["password"])()
                    domain_id = domain_creation["domain"]["id"]
                except:
                    logging.warn(
                        "domain named '%s' doesn't exist and is unable to create." %
                        domain_name)
                    continue
            try:  # fetch record list for domain_name
                records = apicn.RecordList(domain_id=domain_id,
                                           email=account["email"],
                                           password=account["password"])()["records"]
            except:
                logging.error(
                    "fetch record list for domain '%s' failed." %
                    domain_name)
                continue
            record_list = {}
            for per_record in records:
                # only consider A name record
                if per_record["type"].lower() == "a":
                    record_list.update({per_record["name"]: per_record["id"]})
            for sub_domain in account["dns"][domain_name]:
                # gonna create a record for it
                if sub_domain not in record_list:
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
                        logging.error(
                            "fail to create new record '%s' for '%s'" %
                            (sub_domain, domain_name))
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
                        logging.error(
                            "failed to refresh record '%s' at '%s'." %
                            (sub_domain, domain_name))


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format="%(message)s")
    if validation():
        logging.info("config validation passed.")
        sync_domains()
        logging.info("finished.")
