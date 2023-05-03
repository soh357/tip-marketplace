from SiemplifyUtils import output_handler
from SiemplifyConnectors import SiemplifyConnectorExecution
from OverflowManager import OverflowAlertDetails
from SiemplifyConnectorsDataModel import CaseInfo
import SiemplifyUtils
import subprocess

from TestManager1 import TestManager1
from TestManager2 import TestManager2
import pyjokes
import cowsay

import uuid
import sys
import random

#==============================================================================
# This is a Connector Template + mock generator. This file objective is to demonstrate how to build a connector, and exmplain the objective of each field.
# All the data generated here, is MOCK data. Enjoy.
#==============================================================================

GENERATE_ENVIRONMENTS = True



class RandomDataGenerator(object):

    RULE_GENERATOR_FAILED_LOGIN = "Failed login"
    RULE_GENERATOR_OUT_OF_HOURS = "Out of hours activities"
    RULE_GENERATOR_UNAUTHORIZED = "Unauthorized access attempt"
    RULE_GENERATOR_PORT_SCAN = "Port scan"
    RULE_GENERATOR_PHISHING = "Phishing Attempt"

    PRODUCT_AD="Active Directory"
    PRODUCT_IPS = "IPS"
    PRODUCT_PHISHING = "Phishing Email Detector"
    PRODUCT_AV = "AntiVirus"

    SOURCE_GROUPING_IDENTIFIER_A = "A"
    SOURCE_GROUPING_IDENTIFIER_B = "B"
    SOURCE_GROUPING_IDENTIFIER_C = "C"
    SOURCE_GROUPING_IDENTIFIER_D = "D"
    SOURCE_GROUPING_IDENTIFIER_E = "E"



    def __init__(self, is_static):
        self.is_static = is_static

    _vendor = None
    @property
    def VENDOR(self):
        if (not self._vendor or self.is_static == False):
            vendors = ["Macrohard", "Anira", "Mcnally"]
            random_vendor = vendors[random.randint(0, len(vendors) - 1)]
            self._vendor = random_vendor

        return self._vendor


    _source_group_identifier = None
    @property
    def SOURCE_GROUPING_IDENTIFIER(self):
        if (not self._source_group_identifier or self.is_static == False):
            rules = [self.SOURCE_GROUPING_IDENTIFIER_A,
                     self.SOURCE_GROUPING_IDENTIFIER_B,
                     self.SOURCE_GROUPING_IDENTIFIER_C,
                     self.SOURCE_GROUPING_IDENTIFIER_D,
                     self.SOURCE_GROUPING_IDENTIFIER_E]
            random_rule = rules[random.randint(0, len(rules) - 1)]
            self._source_group_identifier = random_rule

        return self._source_group_identifier

    _rule_generator = None
    @property
    def RULE_GENERATOR(self):
        if (not self._rule_generator or self.is_static == False):
            rules = [self.RULE_GENERATOR_FAILED_LOGIN,
                     self.RULE_GENERATOR_OUT_OF_HOURS,
                     self.RULE_GENERATOR_UNAUTHORIZED,
                     self.RULE_GENERATOR_PORT_SCAN,
                     self.RULE_GENERATOR_PHISHING]
            random_rule = rules[random.randint(0, len(rules) - 1)]
            self._rule_generator = random_rule

        return self._rule_generator

    def create_product(self, rule_generator):
        rule_tree = {self.RULE_GENERATOR_FAILED_LOGIN: [self.PRODUCT_AD,self.PRODUCT_IPS],
                     self.RULE_GENERATOR_OUT_OF_HOURS: [self.PRODUCT_AD,self.PRODUCT_IPS],
                     self.RULE_GENERATOR_UNAUTHORIZED: [self.PRODUCT_AD, self.PRODUCT_IPS],
                     self.RULE_GENERATOR_PORT_SCAN: [self.PRODUCT_AV,self.PRODUCT_IPS],
                     self.RULE_GENERATOR_PHISHING : [self.PRODUCT_PHISHING]}
        possible_products = rule_tree[rule_generator]
        random_product = possible_products[random.randint(0, len(possible_products) - 1)]
        return random_product


    def create_alert_name(self,rule_generator, product):

        tree = {self.RULE_GENERATOR_OUT_OF_HOURS: {self.PRODUCT_AD:["Active Directory Audit Policy Warning"],
                                         self.PRODUCT_IPS:["Activity timeline sensor triggered"]},
                self.RULE_GENERATOR_FAILED_LOGIN: {self.PRODUCT_AD:["Active Directory Audit Policy Warning"],
                                         self.PRODUCT_IPS:["User Authentication sensor triggered","unauthorized access detected"]},
                self.RULE_GENERATOR_PORT_SCAN: {self.PRODUCT_AV:["New Port Used","System Service port blocked by unknown process"],
                                                self.PRODUCT_IPS:["Out out policy port used","Unusual Port activity"]},
                self.RULE_GENERATOR_PHISHING: {self.PRODUCT_PHISHING:["Suspisous attachment hash detected in mail","Mail contains a known phishing address"]},
                self.RULE_GENERATOR_UNAUTHORIZED: {self.PRODUCT_AD:["User attempted to access computer out of Group", "'Morgan' vulnrability detected"],
                                                   self.PRODUCT_IPS:["WAF Flag Triggered A54","WAF Flag Triggered B34"]}
                }

        possible_event_names = tree[rule_generator][product]


        #                      "Port scan": ["ClearNet's detected a port scan", "Antivirus detected unusual port traffic"]}

        random_event_name = possible_event_names[random.randint(0, len(possible_event_names) - 1)]

        return random_event_name


    _source_host = None

    ATTACHMENT_A_BLOB64 = "iVBORw0KGgoAAAANSUhEUgAAAGMAAABoCAYAAADl/E5WAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsIAAA7CARUoSoAAAAVQSURBVHhe7Zs/aBtXHMd/5ymaKhlSsCDY2BlsJ5QEZcgQDCl1F5PFtENpCTaYbqZQAhm6GEyGgmkJXQ0xJiVLMAXjpYaICA8dIhJKY2exqEhRhoClTurk63v276TT6U4nnfSefi/v9wHj35NDBn3u931/7s6p/vObCwwJRvA3QwCWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQiWQQjCDz6XYa24D7s4CmcUvptdhLspHBoOLRm1POSOj3HQK+aLoSGjLwnt3JlagbU0DgxiyDK6iaKEZOahODmOAzMY3gQuu0GVCEl1H3KHr4RucxhOZ3QbS7FXd3xnmRRZ+mXEikg4EddfwTeHL+AIhx4z2S/g8ZgZNjTHlLiSO4iQX1wxl3BFlLoGj3MrUJy9ATP4kWlolVEoRUeKjJOBXMEoZSc7eja8nDJnWaUvpjrEk6lL0UGjqTNqsF0JFyGjiUWco0dG7SU8rGPtJ3UDHhgyuepAi4zCSUQ8Za+BWdsytWiQUYZnVSz9iK5Y5qZoQb2MWil0BTWTmeCuCKBcRrke1haj8Hma2yKIYhk1eF49wdpPBiY+kHsQg0SxjH+hFLqKynBEhaBhAg/hAssIQ+0OfCCHd33c8xArtp1Zc5bPw+mMXohYjXVF/QU8qmFtAPRlWAR9GelJuIPlh85Q5gw196drsH34tO0MzKQTYbWdIZawl7Fk4lEcUx/BZNjm7r+qUQ8K6EKxjDRMXMDST70Ez8M2g5ajfAIfT53f/mzlBH6vGbTm1IQGGRmsWjmq/s1RFUC5jMilqWEbMh2olwHjsIxPagTZrZj1xJ9qNMgQOkR3hD7LJLrjh3fcHh5aZMhnmb4NnzrgqPIMtnlldYYeGYK5sagn/U7g4eEOCxFokyG740HE3HEuZBPWLE8sfTIE42OL8HNEXEl2jzchV8xDAce9UCi1n0uZxhBeCQg/0Asl7kCxi1cL+JWAWHoQ0id8ahtLGu7ONp8UV8cUfGrQE0FD6gw/at7rM+klGQ8CMjwGEV2KXz9+m4fTL/dw4GP1Pox8fREHySEko5Xyux1YrIQ9ANeKlg44eAKn94o4iCIHzh9fgYOjJJCVQYf34C79CO4bWQe/8Nfg3nwEjS9wegFGtm7joHeGNIGbh7OxASNtV/4VIWe5+dmbPXAPsE4Ay4jlIjhbG+DcwmEbVwAWsBS45fdY9Y4dMn79CU5v3jv7ibty3fXzf3e6lMdP4nEms1j1hx0y5q5jIb7s/GuswhB/8xZLUx9joQ87ZFy6Cs401nt/NifcIAfNvzm3Rfx0hZjg9ytYZ8GZS77EtWTOELk/70WJWKJGRJWb95avOYDIOSLA279wpSWYvg7OJawTYM8EHhtVvoha/azr/YK75dsEzl/FIhn2yIiLqkZE9RA1YjPoei7kHqPPXbg9MmRUrYj4OSMYVSL3NzGiuo4aseFr7MqFwPXkmz0Pi2QIbn3SiJ+WqPLnfldR07rzdja+72uu8LBLhn+D5o+qwkssuokoeTziOwJZvd9hQ9gblsmQS9ZgVPmWprER5T+nEgzotNbDOhltUeWLKGelU+6rFSGxT0YwqhoR1Xlv4a6rFSGxUIbogCXPRhHcXzCiFpodE0SeVzWWsAvLSkRILL2fEYgcgTwiD52Io+7udSDy/4rBys5oPR6R9HD8oRC+00cISzuDJiyDECyDECyDECyDECyDECyDECyDECyDECyDECyDECyDECyDECyDDAD/A+CNxriJKoq1AAAAAElFTkSuQmCC"
    ATTACHMENT_B_BLOB64 = "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CjQ4ClsKNjY5Cl0KNDkKMzk4CjAKMzk5ClsKNTkwCl0KNDAwCjQyNwowCjQyOApbCjU2MwpdCjQyOQo0NDEKMAo0NDIKWwo2MDQKXQo0NDMKNDc2CjAKNDc3ClsKNjc3Cl0KNDc4CjUwNwowCjUwOApbCjI2OQpdCjUwOQo1MTYKMAo1MTcKWwoxMDYxCjAKNjc3Cl0KNTIwCjU2NAowCjU2NQpbCjY3OApdCjU2Ngo1ODkKMAo1OTAKWwo0MDYKXQo1OTEKNjI3CjAKNjI4ClsKNTM0Cl0KXQo+PgplbmRvYmoKMTcKMApvYmoKPDwKL1R5cGUKL0ZvbnREZXNjcmlwdG9yCi9Gb250TmFtZQovTVVGVVpZK01vbnRzZXJyYXQtUmVndWxhcgovRmxhZ3MKNAovRm9udEJCb3gKWwotODIzCi0yNjIKMTU4NgoxMDQzCl0KL0FzY2VudAo5NjgKL0Rlc2NlbnQKLTI1MQovSXRhbGljQW5nbGUKMAovQ2FwSGVpZ2h0CjcwMAovU3RlbVYKODAKL0ZvbnRGaWxlMgoxOAowClIKPj4KZW5kb2JqCjE5CjAKb2JqCjI5NQplbmRvYmoKMjAKMApvYmoKNTkyNgplbmRvYmoKMQowCm9iago8PAovVHlwZQovUGFnZXMKL0tpZHMKWwo2CjAKUgpdCi9Db3VudAoxCj4+CmVuZG9iagp4cmVmCjAgMjEKMDAwMDAwMDAwMiA2NTUzNSBmIAowMDAwMDA4NTc3IDAwMDAwIG4gCjAwMDAwMDAwMDMgMDAwMDAgZiAKMDAwMDAwMDAwMCAwMDAwMCBmIAowMDAwMDAwMDE2IDAwMDAwIG4gCjAwMDAwMDAxNjAgMDAwMDAgbiAKMDAwMDAwMDIwNyAwMDAwMCBuIAowMDAwMDAwMzczIDAwMDAwIG4gCjAwMDAwMDExNDUgMDAwMDAgbiAKMDAwMDAwMDk5MCAwMDAwMCBuIAowMDAwMDAxMDA5IDAwMDAwIG4gCjAwMDAwMDEwMjkgMDAwMDAgbiAKMDAwMDAwMTA2NyAwMDAwMCBuIAowMDAwMDAxMTExIDAwMDAwIG4gCjAwMDAwMDEzMzIgMDAwMDAgbiAKMDAwMDAwNzg2MCAwMDAwMCBuIAowMDAwMDAxNDg3IDAwMDAwIG4gCjAwMDAwMDgzMjggMDAwMDAgbiAKMDAwMDAwMTg1OCAwMDAwMCBuIAowMDAwMDA4NTM2IDAwMDAwIG4gCjAwMDAwMDg1NTYgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZQoyMQovUm9vdAo0CjAKUgovSW5mbwo1CjAKUgo+PgpzdGFydHhyZWYKODYzNgolJUVPRgo="
    ATTACHMENT_C_BLOB64 = "VGV4dCBFeGFtcGxlLCB3aHk/IHdoYXQgZGlkIHlvdSBleHBlY3Q/"
    def create_random_alert_attachment(self):
        attachments = [{"base64_blob" : self.ATTACHMENT_A_BLOB64,
                        "type" : "png",
                        "name" : "G2",
                        "description" : "G2 Icon for for testing attachments via case info",
                        "is_favorite" : False},
                       {"base64_blob": self.ATTACHMENT_B_BLOB64,
                        "type": "pdf",
                        "name": "AttachmentExample",
                        "description": "Slide converted into pdf for testing attachments via case info",
                        "is_favorite": False},
                       {"base64_blob": self.ATTACHMENT_C_BLOB64,
                        "type": "txt",
                        "name": "ExampleTest",
                        "description": "text file converted writen manualy and with love for testing attachments via case info",
                        "is_favorite": True}
                       ]

        random_attachment = attachments[random.randint(0, len(attachments) - 1)]
        return random_attachment

    @property
    def SOURCE_HOST(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._source_host or self.is_static == False):
            self._source_host = "Src_Host_" + str(random.randint(0, 10))
        return self._source_host

    _dest_host = None

    @property
    def DEST_HOST(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._dest_host or self.is_static == False):
            self._dest_host = "Dst_Host_" + str(random.randint(0, 10))
        return self._dest_host

    _source_ip = None
    @property
    def SOURCE_IP(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._source_ip or self.is_static == False):
            self._source_ip = "10.0.0." + str(random.randint(0, 50))
        return self._source_ip

    _dest_ip = None
    @property
    def DESTINATION_IP(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._dest_ip or self.is_static == False):
            self._dest_ip = "200.0.0." + str(random.randint(0, 50))
        return self._dest_ip

    _source_username = None
    @property
    def SOURCE_USERNAME(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._source_username or self.is_static == False):
            self._source_username = "src_user_" + str(random.randint(0, 50))
        return self._source_username

    _destination_username = None
    @property
    def DESTINATION_USERNAME(self):
        if (random.randint(0, 5) == 0): return None
        if (not self._destination_username or self.is_static == False):
            self._destination_username = "dst_user_" + str(random.randint(0, 50))
        return self._destination_username

    _usb = None
    @property
    def USB(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._usb or self.is_static == False):
            self._usb = "usb_" + str(random.randint(0, 300))
        return self._usb

    _filename = None
    @property
    def FILENAME(self):
        if (random.randint(0, 3) == 0): return None
        if (not self._destination_username or self.is_static == False):
            self._filename = "filename" + str(random.randint(0, 50))+".txt"
        return self._filename

    _filehash = None
    @property
    def FILEHASH(self):
        if (random.randint(0, 4) == 0): return None
        if (not self._destination_username or self.is_static == False):
            hashes = ["bb9d72654ab021561cef4c38ae0f8999",
                     "ba22d18e50b1dd3816234194f1ec80d0",
                     "3283e1a9cc738526842c195a862a8b14",
                     "4da2687190b4fb0986c30e7b048c34c1",
                     "08c75a8fb8010d5b68dde217f92fe84e",
                     "c2e39d563dd537288f441643e334f6b9",
                     "d4b4e9b2cdff02ac0f5c6bf7cb878c49",
                     "f881b4cfbf549405f830a2f1cd2ba2d7",
                     "29dad148591bf98df950f6071ff014b9"]
            self._filehash = hashes[random.randint(0, len(hashes) - 1)]
        return self._filehash

    _destinationPort = None
    @property
    def PORT(self):
        if (random.randint(0, 2) == 0): return None
        if (not self._destination_username or self.is_static == False):
            self._destinationPort = str(random.randint(1, 9000))
        return self._destinationPort

    _categoryOutcome = None
    @property
    def CATEGORY_OUTCOME(self):
        if (not self._destination_username or self.is_static == False):
            outcomes = ["Blocked",
                      "Approved",
                      "Rejected",
                      "Passed",
                      "Proxied",
                      "Unified",
                      "Eliminited",
                      "Exterminiated",
                      "Quarantined"]
            self._categoryOutcome = outcomes[random.randint(0, len(outcomes) - 1)]
        return self._categoryOutcome

class DummyGenerator(object):
    SOURCE = "DummyGenerator"

    def __init__(self,logger):
        self.LOGGER = logger
        self.GENERATOR = RandomDataGenerator(is_static=True)

    def BuildDummySecurityEvent(self,environment, rule_generator, product):
        event = {}

        # Fill event fields by BL logic here:
        # Here is an exmaple of fields usually found in siems:

        # Time Fields (Arcsight Example):
        event["managerReceiptTime"] = SiemplifyUtils.unix_now() # Times should be saved in UnixTime. You may use SiemplifyUtils DateTime conversions, or the example convert_datetime_to_unix_time method below
        event["StartTime"] = SiemplifyUtils.unix_now()
        event["EndTime"] = SiemplifyUtils.unix_now()
        event["Environment"] = environment

        # Some fields, siemplify expects as mandatory. Their names may vary in source, but later on they will be mapped:
        alert_type = self.GENERATOR.create_alert_name(rule_generator,product)
        event["event_type"] = alert_type
        event["name"] = alert_type + " " + str(SiemplifyUtils.unix_now())
        event["device_product"] =  product# ie: "device_product" is the field name in arcsight that describes the product the event originated from.

         # usually, the most intresting fields are (again, their precise name, may vary between siems.
        # You are not expected to fill them yourself, just pass them along from the siem. Since this is a dummy generator, We create them manaualy with made up name (PascalCase\CcmelCase doesn't matter)
        event["SourceHostName"] = self.GENERATOR.SOURCE_HOST
        event["DestinationHostName"] = self.GENERATOR.DEST_HOST
        event["SourceAddress"] = self.GENERATOR.SOURCE_IP
        event["DestinationAddress"] = self.GENERATOR.DESTINATION_IP
        event["SourceUserName"] = self.GENERATOR.SOURCE_USERNAME
        event["DestinationUserName"] = self.GENERATOR.DESTINATION_USERNAME
        event["FileName"] = self.GENERATOR.FILENAME
        event["Usb"] = self.GENERATOR.USB
        event["FileHash"] = self.GENERATOR.FILEHASH
        event["Port"] = self.GENERATOR.PORT
        event["CategoryOutcome"] = self.GENERATOR.CATEGORY_OUTCOME

        non_empty_event = {}
        for key in event:
            if (event[key]):
                non_empty_event[key]=event[key]

        # It is also usual, for extra data, to be available, or fetched from the siem. What it is you want. ie:
        # event["IsMalicousByVirusTotal"] =
        # event["PaloAlto_AutoFocus_Tags"] =

        return non_empty_event

    def GenerateDummyCase(self, siemplify, environment):

        # We start by creating a caseInfo object. This represent a siemplify "Alert".
        # An alert, is the siems build in aggregation of basic event ie (Arcsight correlation or QRadar Offense)
        case_info = CaseInfo()
        case_info.events = []
        case_info.source_grouping_identifier = self.GENERATOR.SOURCE_GROUPING_IDENTIFIER
        # each case_info object, must have a uniqe key. The objective of this, is to later validate the same data isn't digested multiple times, creating duplicates in the system.
        # The key is later on built by "Name' + 'TicketId' fields Combination. Make sure its a unique combination! (ie: Arcsight will use: CorrelationName+EventId. QRadar will use: OffenseName+OffenseId)
        # The uniqueness must be persistant, even after Server Restart\ Refetching of the same that from siem, multiple runs of the same API queries, etc.
        case_info.ticket_id = str(uuid.uuid4())  # The ID of the siem alert. Should be the extact ID as saved and identified in the siem. (ie: Arcsight Correlation's EventId, or QRadar OffenseId).

        case_info.rule_generator = self.GENERATOR.RULE_GENERATOR  # Describes the name of the siem's rule, that caused the aggregation of the alert.
        case_info.name =  case_info.rule_generator + " " + str(SiemplifyUtils.unix_now())
        case_info.device_product = self.GENERATOR.create_product(case_info.rule_generator) # This field, may be fetched from the Original Alert. If you build this alert manualy, Describe the source product of the data. (ie: ActiveDirectory, AntiVirus)
        # ----------------------------- Base Events Populating START -----------------------------
        # Build case events here, heres a mock example:
        # First, we wil populate the alert with events:



        for i in range(0,2):
            random_event = self.BuildDummySecurityEvent(environment, case_info.rule_generator, case_info.device_product)
            case_info.events.append(random_event)
        # ----------------------------- Base Events Populating END -----------------------------


        # ----------------------------- Alert Field initilization START -----------------------------


        case_info.environment = environment

        # The alert times may be fetched as the original data of the alert, or recalculated as the minimum+maxsimum times of BaseEvents.
        case_info.start_time =  SiemplifyUtils.unix_now() # Times should be saved in UnixTime. You may use SiemplifyUtils DateTime conversions
        case_info.end_time =  SiemplifyUtils.unix_now()

        # Cases Priority are Calculated by the siemplify Server Algorithem. But, sometimes, the feature may be turned off (To preserve original siem priority).
        # In case this may happen, it is advised to set a default priority value before hand.
        case_info.priority =  60 # Informative = -1,Low = 40,Medium = 60,High = 80,Critical = 100.

        case_info.device_vendor = self.GENERATOR.VENDOR # This field, may be fetched from the Original Alert. If you build this alert manualy, Describe the source vendor of the data. (ie: Microsoft, Mcafee)
        case_info.attachments = [self.GENERATOR.create_random_alert_attachment()]
        # ----------------------------- Alert Field initilization END -----------------------------

        return case_info


@output_handler
def main():
    # Connectors are run in iterations. The interval is configurable from the ConnectorsScreen UI.
    start_timestamp = SiemplifyUtils.unix_now()
    output_variables = {}

    cases = [] # The main output of each connector run
    siemplify = SiemplifyConnectorExecution() # Siemplify main SDK wrapper
    

    # ------------ Logging ----------------------
    # It is best to use this logger. It's output will be visible at:
    # "C:\Siemplify_Server\Scripting\SiemplifyConnectorExecution\<Connector's instance name>\logdata.log"
    # "http://localhost:5601 -- default kibana service
    # It is possible to pass the logger class other classes.
    siemplify.LOGGER.info("----Mock Template - Main - STARTED-------")
    # Last logging call must be performed before calling "return_package"

    # log_items is a depricated logging system. each item is a string record. It is passed along via the sdtout, after calling the "return_package" method, So size should be considered.
    # This logs will be passed along the the siemplify server DB, if feature is turned on, via the connector framework.
    log_items = []  #
    # ------------ Logging ----------------------

    # the params passed along from the Framework (as set in the IDE \ Connector screen UI. Can be used to create a more configurable logic, are simply, pass dynamic arguments (ie: Server IP + Credentials)
    params = siemplify.parameters
    siemplify.LOGGER.info("PARAMS:" + str(params))

    # For MSSP, each alert and its baseEvents, will be part of a diffrenet customer environment. In Arcsight, it is distinguished by the "customer_uri" field. Here we create a random:
    environments = ["AAA", "BBB", "CCC"]
    random_environment = environments[random.randint(0, len(environments) - 1)]

    if (GENERATE_ENVIRONMENTS==False):
        random_environment = None

    dummyCon = DummyGenerator(siemplify.LOGGER)
    dummyCase = dummyCon.GenerateDummyCase(siemplify,random_environment)

    # overflow, is a configurable mechanism to limit alert digested by the system, based on a 3 way key (environment, product, ruleGenreator (alertName)
    is_overflow = siemplify.is_overflowed_alert(environment=random_environment,
                                                alert_identifier=str(dummyCase.ticket_id),
                                                #ingestion_time=str(SiemplifyUtils.unix_now()),
                                                #original_file_path=None,
                                                #original_file_content=None,
                                                alert_name=str(dummyCase.rule_generator),
                                                product=str(dummyCase.device_product)
                                                #source_ip=None,
                                                #source_host=None,
                                                #destination_ip=None,
                                                #destination_host=None
                                                )

    if (is_overflow):
        siemplify.LOGGER.warn("Alert {} has overflowed".format(dummyCase.ticket_id), module="DummyConnector", alert_id=dummyCase.ticket_id)
    else:
        cases.append(dummyCase)
        siemplify.LOGGER.info("Alert {} processed by DummyConnector".format(dummyCase.ticket_id), module="DummyConnector", alert_id=dummyCase.ticket_id)

    end_timestamp = SiemplifyUtils.unix_now()
    runtime_ms = end_timestamp-start_timestamp
    siemplify.LOGGER.info("----Mock Template - Main - FINISHED-------",module="OverflowMockConnector",alert_id=dummyCase.ticket_id,miliseconds=runtime_ms)
    # At the and, call the Return_package, to return the result of the connector run, from the python scrpit, back to the Framework.
    siemplify.return_package(cases, output_variables, log_items)


@output_handler
def Test():
    # This method, is called when clicking the Test button in the IDE \ Connector screen UI's
    # This method objective is to validate the connector is ready to run. Here is the place to perform connectivty, credentials, and params test.

    # ------------------ Test Logic - Start -----------------------
    siemplify = SiemplifyConnectorExecution()
    siemplify.LOGGER.info("----Mock Template - Test - STARTED-------")

    if str(siemplify.parameters.get("Fail", "False")).lower() == "true":
        raise Exception("ERROR")

    siemplify.LOGGER.info("------------------TEST DEPENDENCIES & MANAGERS COUPLING------------------")

    t1 = TestManager1()
    assert t1.get_version() == "A1"

    t2 = TestManager2()
    assert t2.get_version() == "A2"

    cowsay.cheese("YAY")
    siemplify.LOGGER.info(pyjokes.get_joke())

    assert pyjokes.__version__ == "0.5.0"
    proc = subprocess.Popen("pip freeze", stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    assert "cowsay==2.0.3" in out
    siemplify.LOGGER.info("------------------FINISHED TEST DEPENDENCIES & MANAGERS COUPLING------------------")


    siemplify.LOGGER.info("------------------TEST CONNECTOR PARAMS------------------")
    
    boolean = str(siemplify.parameters.get("Boolean", "False")).lower() == 'true'
    integer = int(siemplify.parameters.get("Integer", 0)) if siemplify.parameters.get("Integer") else 0
    password = siemplify.parameters.get("Password")
    string = siemplify.parameters.get("String")
    ip = siemplify.parameters.get("IP")
    email = siemplify.parameters.get("Email")
    user = siemplify.parameters.get("User")
    stage = siemplify.parameters.get("Stage")
    case_close_reason = siemplify.parameters.get("Case Close Reason")
    close_case_root_cause = siemplify.parameters.get("Close Case Root Cause")
    priority = siemplify.parameters.get("Priority")
    email_content = siemplify.parameters.get("Email Content")
    content = siemplify.parameters.get("Content")
    playbook_name = siemplify.parameters.get("Playbook Name")
    entity_type = siemplify.parameters.get("Entity Type")
    lst = siemplify.parameters.get("List")
    
    siemplify.LOGGER.info("Boolean: {}".format(boolean))
    siemplify.LOGGER.info("Integer: {}".format(integer))
    siemplify.LOGGER.info("Password: {}".format(password))
    siemplify.LOGGER.info("String: {}".format(string))
    siemplify.LOGGER.info("IP: {}".format(ip))
    siemplify.LOGGER.info("Email: {}".format(email))
    siemplify.LOGGER.info("User: {}".format(user))
    siemplify.LOGGER.info("Stage: {}".format(stage))
    siemplify.LOGGER.info("Case Close Reason: {}".format(case_close_reason))
    siemplify.LOGGER.info("Close Case Root Cause: {}".format(close_case_root_cause))
    siemplify.LOGGER.info("Priority: {}".format(priority))
    siemplify.LOGGER.info("Email Content: {}".format(email_content))
    siemplify.LOGGER.info("Content: {}".format(content))
    siemplify.LOGGER.info("Playbook Name: {}".format(playbook_name))
    siemplify.LOGGER.info("Entity Type: {}".format(entity_type))
    siemplify.LOGGER.info("List: {}".format(lst))
    
    siemplify.LOGGER.info("------------------FINISHED TEST CONNECTOR PARAMS------------------")
    
    # result_params is a free-form dictionary, that will be presented in the UI after clicking the Test button.
    # You may place here whatever you want. Here is an mock example
    result_params = {}
    result_params["Params Validation"] = "Valid" # ie: Valid, Missing Mandatory, Invalid Values,
    result_params["Connectivity Validation"] = "No Ping" # ie: Success, No Ping, No endpoint listening, Timeout, HTTP ErrorCodes
    result_params["Credentials Validation"] = "Valid" # ie: Wrong Username\Password
    result_params["Data Fetching"] = "Valid" # ie: Success, Autherization Problem, No Data, Invalid Query Syntax

    success = True # simple Yes no Anser for Connector Test Success status:

    # overflow, is a configurable mechanism to limit alert digested by the system, based on a 3 way key (environment, product, ruleGenreator (alertName)
    is_overflow = siemplify.is_overflowed_alert(environment="TEST ENV",
                                                alert_identifier="TICKET_ID",
                                                alert_name="RULE_GEN",
                                                product="PRODUCT")

    siemplify.LOGGER.info("----Mock Template - Test - FINISHED-------")
    # ------------------ Test Logic - End -----------------------

    siemplify.return_test_result(success, result_params)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == 'True':
        print "Starting Main Execution"
        main()
    else:
        print "Starting Test Execution"
        Test()