import requests
import os
import sys
import json
import uuid
import time
from datetime import datetime, timedelta
import urllib.parse
import urllib


def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        sys.exit(1)

    return env_value

def get_services_by_escalation_policy_id(escalation_policy_id, pagerduty_user_token):
    response = requests.get("https://api.pagerduty.com/escalation_policies/%s" % escalation_policy_id,
                            headers=get_headers(pagerduty_user_token))

    status_code = response.status_code
    if status_code != 200:
        raise Exception("Failed to invoke escalation_policies api: " + status_code + " content: " + response.content)

    data = json.loads(response.content)

    services = data['escalation_policy']['services']
    service_ids = [service['id'] for service in services]
    print("Serviceids for escalation policy: %s are: %s" % (escalation_policy_id, str(service_ids)))
    return service_ids

def getTimeRange():
    endTime = datetime.utcnow()
    # startTime = datetime.utcnow() - timedelta(hours=12)
    startTime = datetime.utcnow() - timedelta(hours=168)
    return (startTime, endTime)

def get_headers(pagerduty_user_token):
    return {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token=%s' % pagerduty_user_token
    }

def get_pagerduty_timeformat(targetDateTime):
    return targetDateTime.strftime("%Y-%m-%dT%H:%M:%S")

# def print_curl_version(response):
#     req = response.request
#     command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
#     method = req.method
#     uri = req.url
#     data = req.body
#     headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
#     headers = " -H ".join(headers)
#     print(command.format(method=method, headers=headers, data=data, uri=uri))

def request_pagerduty_events(startTime, endTime, service_id, offset, limit, pagerduty_user_token):

    query_parameters = {
        "limit": limit,
        "service_ids[]": service_id,
        # "service_ids[]": ",".join(service_ids_list),
        "time_zone": "UTC",
        "since": get_pagerduty_timeformat(startTime),
        "until": get_pagerduty_timeformat(endTime),
        "offset": offset
    }
    payload_str = urllib.parse.urlencode(query_parameters)

    response = requests.get("https://api.pagerduty.com/incidents",
                            params=payload_str,
                            headers=get_headers(pagerduty_user_token))

    # print_curl_version(response)

    if response.status_code == 200:
        # TODO: remove the sleep from here
        time.sleep(2)
        # print(response.content)
        return response.content

    raise Exception("Got non-200 response from pagerduty api")


def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)

def pull_pagerduty_events(startTime, endTime, service_id, pagerduty_user_token, json_drop_directory):
    hasMoreEvents = True
    offset = 0
    limit = 50
    while hasMoreEvents:
        print("Requesting with offset: " + str(offset))
        raw_response = request_pagerduty_events(startTime=startTime, endTime=endTime,
                                            service_id=service_id, offset=offset,
                                            limit=limit, pagerduty_user_token=pagerduty_user_token)

        response = json.loads(raw_response)
        offset = offset + limit
        hasMoreEvents = response['more']
        file_name = os.path.join(json_drop_directory, "%s-%d.json" % (service_id, offset))
        write_to_file(file_name=file_name, content=json.dumps(response, indent=4))

if __name__ == "__main__":
    pagerduty_user_token = pull_env_var("PD_USER_TOKEN")
    escalation_policies = pull_env_var("PD_ESC_POLICIES_CSV")

    service_ids_list = list()

    escalation_policies_list = escalation_policies.split(",")

    for escalation_policy_id in escalation_policies_list:
        service_ids = get_services_by_escalation_policy_id(escalation_policy_id, pagerduty_user_token)
        service_ids_list.extend(service_ids)

    # time format: 2021-03-01T14:04:35

    drop_directory = os.path.join(os.getcwd(), str(uuid.uuid4()))
    print("Drop directory is: " + drop_directory)
    os.mkdir(drop_directory)

    (startTime, endTime) = getTimeRange()

    total_services = len(service_ids_list)
    current = 0

    for service_id in service_ids_list:
        pull_pagerduty_events(startTime=startTime,endTime=endTime,
                              service_id=service_id,
                              pagerduty_user_token=pagerduty_user_token,
                              json_drop_directory=drop_directory)
        current += 1
        print("Done: %d total: %d" % (current, total_services))