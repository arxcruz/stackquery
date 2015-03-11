import requests
import json

GERRIT_URL = 'https://review.openstack.org'


def get_changes_by_filter(search_filter):
    changes = '/changes/?q=%s&o=CURRENT_REVISION&o=DETAILED_ACCOUNTS' % search_filter
    ret_val = requests.get(GERRIT_URL + changes)
    ret_val.raise_for_status()
    text = ret_val.text
    # For some reason, the REST api are bringing the characteres
    # )]}' in the beginning which make ret_val.json() fails
    text = text.replace(')]}\'', '')
    return json.loads(text)