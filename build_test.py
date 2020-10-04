# creating a mock service with the pact
# ultimately the pact file will be written to pact_dir
# and published to broker if publish_to_broker is set to TRUE

import unittest
import client
import atexit
import logging
from pact import Consumer, Provider
import json
from requests.auth import HTTPBasicAuth
import requests

pact = Consumer('Consumer').has_pact_with(Provider('Provider'),pact_dir='./pact/pacts',log_dir="./log",port=1234,host_name='localhost')
pact.start_service()
atexit.register(pact.stop_service)

PACT_FILE="./pact/pacts/consumer-provider.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
#PACT_UPLOAD_URL = ("https://ellialderson.pactflow.io/pacts/provider/Provider/consumer/Consumer/version")
PACT_LOCAL_UPLOAD_URL = ("http://192.168.99.114/pacts/provider/Provider/consumer/Consumer/version")

class GetBuildInfoContract(unittest.TestCase):

    mock_host='http://localhost:1234' # this is the mock service just like CM-Persistence

    def test_get_build(self):

        true = True
        expected = {u'name': u'#345',u'completed': true,u'info': {u'coverage': 30,u'apiversion': 0.1,u'swaggerlink': u'http://swagger',u'buildtime': 230}}

        '''
         adding interaction just like in golang
         these will be our expected interactions
        '''
        '''
        writing expectations from the mock service
        '''
        (pact
        .given('build 3455 exists')
        .upon_receiving('a request for build 3455')
        .with_request('get', '/builds/3455')
        .will_respond_with(200, body=expected))

        pact.setup()
        with pact:
            '''
            client.build is redundant again here, instead you
            could have directly called the mock-service
            result = requests.get('http://localhost:1234/builds/3455')
            '''
            result = client.build(self.mock_host,3455)

        self.assertEqual(result, expected)
        '''
            self.assertEqual(result.json(),expected)
        '''
        push_to_broker('2.0.0')
        pact.verify()

'''
the below method push_to_broker becomes redundant, instead
has_pact_with() method in Consumer class has parameters like
-> publish_to_broker = True,
-> broker_base_url = "http://192.168.99.114:80",
-> broker_username = "pactbroker",
-> broker_password = "pactbroker"
'''
def push_to_broker(version):
    with open(PACT_FILE,'rb') as pact_file:
        pact_file_json = json.load(pact_file)

        basic_auth = HTTPBasicAuth(PACT_BROKER_USERNAME,PACT_BROKER_PASSWORD)
        logging.info("uploading file to pact broker")
        #headers = {"Authorization": "Bearer 0rdrGK1q82jx0bbnf7f7zQ"}
        #r= requests.put(
        #    "{}/{}".format(PACT_UPLOAD_URL,version),json=pact_file_json,headers=headers
        #)
        r = requests.put(
            "{}/{}".format(PACT_LOCAL_UPLOAD_URL,version),json=pact_file_json,auth=basic_auth
        )
        if not r.ok:
            logging.error("Error uploading : %s",r.content)
            r.raise_for_status()
