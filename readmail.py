#-------------------------------------------------------------------------------
# Name:        readmail
# Purpose:
#
# Author:      krh5058
# Version:     Python 3.3
# Created:     17/04/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#------------------------------------------------------------------------------

"""Utilities for HEFCalApp.

Utilities for parsing web form data from a GMail account
"""

__author__ = 'ken.r.hwang@gmail.com (Ken Hwang)'

import imaplib
import base64
import pprint
##from imaplib_connect import open_connection
##import email
import re
import sys

##def extract_body(payload):
##    if isinstance(payload,str):
##        return payload
##    else:
##        return '\n'.join([extract_body(part.get_payload()) for part in payload])

##def open_connection(verbose=False):
##    # Read the config file
##    config = ConfigParser.ConfigParser()
##    config.read([os.path.expanduser('~/.pymotw')])
##
##    # Connect to the server
##    hostname = config.get('server', 'hostname')
##    if verbose: print 'Connecting to', hostname
##    connection = imaplib.IMAP4_SSL(hostname)
##
##    # Login to our account
##    username = config.get('account', 'username')
##    password = config.get('account', 'password')
##    if verbose: print 'Logging in as', username
##    connection.login(username, password)
##    return connection
##
##list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
##
##def parse_list_response(line):
##    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
####    mailbox_name = mailbox_name.strip('"')
##    return (flags, delimiter, mailbox_name)

def get_keylib(n):
    """Return a pre-defined key value based on 'keylib' index
    """
    keylib = ['MSG_ID', \
    'STUDY_ID', \
    'EXPERIMENTER', \
    'SCHEDULER', \
    'SCHEDULER_EMAIL', \
    'PARTICIPANT_ID', \
    'NUM_OF_SESSIONS', \
    'SESSION_LENGTH', \
    'PARKING_PASS', \
    'TESTING_ROOM', \
    'OTHER_SYSTEMS', \
    'HEF_RA', \
    'IF_NO_HEF_RA', \
    'COMMENT']
    return keylib[n]

print('Connecting...')
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login("heflab", "") # Insert password (string) in second argument

try:
    print('Selecting all mail...')
    typ, mailbox_data = conn.select('"[Gmail]/All Mail"')
    print('Server response:', typ)
    print('Searching in mailbox...')
    typ, msg_ids = conn.search(None, '(FROM "webteam" SUBJECT "HEF Scheduling Request" UNSEEN)')
    msg_ids = msg_ids[0].decode(encoding='UTF-8')
    print ('Server response:', typ)
    if not msg_ids:
        print('No mail for that criteria.')
    else:
        print ('Mail found.  Listing by ID...')
        count = 0
        requests = {}
        for id in [i.strip() for i in msg_ids.split(' ')]:
            print("-------------------")
            print("Message ID:", id)

            request_entry = {} ## Generate entry dict
            request_entry[get_keylib(0)] = id

            ## Header data
            typ, head_data = conn.fetch(id, '(BODY.PEEK[HEADER] FLAGS)')
            head_data = head_data[0][1].decode(encoding='UTF-8').split('\r\n')
            for line in head_data:
                if re.match('To|From|Subject|Date',line):
                        pprint.pprint(line)

            ## Body data
            typ, msg_data = conn.fetch(id, '(BODY.PEEK[TEXT] FLAGS)')
            msg = msg_data[0][1].decode(encoding='UTF-8') ## Decode string as UTF-8
            msg = base64.b64decode(msg).decode(encoding='UTF-8') ## Deconde body text as base64
            msg = msg.split('\r\n') ## Split lines

            ## Parse body data
            for i in range(len(msg)):
                ## Search with tags to avoid finding non-header tag text
                if re.search(r'<dt>Study ID</dt>',msg[i]):
                    n = 1
                elif re.search(r'<dt>Experimenter Name</dt>',msg[i]):
                    n = 2
                elif re.search(r'<dt>Scheduler Name</dt>',msg[i]):
                    n = 3
                elif re.search(r'<dt>Scheduler Email Address</dt>',msg[i]):
                    n = 4
                elif re.search(r'<dt>Participant ID code</dt>',msg[i]):
                    n = 5
                elif re.search(r'<dt># of Sessions Required</dt>',msg[i]):
                    n = 6
                elif re.search(r'<dt>Session Length</dt>',msg[i]):
                    n = 7
                elif re.search(r'<dt>Parking Pass</dt>',msg[i]):
                    n = 8
                elif re.search(r'<dt>Testing Room</dt>',msg[i]):
                    n = 9
                elif re.search(r'<dt>Other Systems</dt>',msg[i]):
                    n = 10
                elif re.search(r'<dt>HEF RAs',msg[i]):
                    n = 11
                elif re.search(r'<dt>If no HEF RA...</dt>',msg[i]):
                    n = 12
                elif re.search(r'<dt>Comments</dt>',msg[i]):
                    n = 13
                else:
                    n = None

                ## Parse and store field
                if n:
                    tmp = re.sub(r'<(dd|/dd|br /|div|/div)>',"",msg[i+1]) ## Remove HTML tags
                    field = tmp.lstrip() ## Strip leading spaces
                    key = get_keylib(n)
                    print(key,'-', field)
                    request_entry[key] = field

            ## Create
            requests[count] = request_entry

            count = count + 1
##        typ, response = conn.store(num, '+FLAGS', r'(\Seen)')

finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()

##if __name__ == '__main__':
##  main(sys.argv)