"""
Based mostly on https://github.com/jpulec/django-protractor, with modifications to run
multiple test cases, and handle a server process for the static SPA in addition to the API server.
"""

import os
from datetime import datetime
import requests
import signal
import subprocess
import sys
import time


BASE_TEST_DIR = 'testing/e2e/'

POLLING_TIMEOUT = 7
POLLING_INTERVAL = .5


class TimeoutException(Exception):
    pass


ELEMENT_EXPLORER = False
if os.environ.get("ELEMENT_EXPLORER"):
    ELEMENT_EXPLORER = True
    del os.environ['ELEMENT_EXPLORER']


class SPAIntegrationTestCaseMixin(object):
    protractor_conf = 'testing/conf.js'
    suite = None
    specs = None
    live_server_url = 'http://localhost:{}/'.format(os.environ.get('STATIC_SERVER_PORT'))
    static_server_command = 'divshot s -p $STATIC_SERVER_PORT'
    test_log_location = os.environ.get('TESTING_LOG_LOCATION', '.logs/testing')
    if not os.path.exists(test_log_location):
        os.makedirs(test_log_location)

    @classmethod
    def setUpClass(cls):
        """If you want to have access to objects you've created in the database in your setUpClass
        method on your subclass when using elementExplorer, call
        super(YourTests, cls).setUpClass() **at the end** of your setUpClass method instead of at
        the beginning."""
        super(SPAIntegrationTestCaseMixin, cls).setUpClass()
        cls.start_static_server()
        cls.start_webdriver()
        cls.poll_until_servers_up()

        # optionally run elementExplorer
        if ELEMENT_EXPLORER:
            print "Pausing for element explorer... "
            subprocess.call("protractor --elementExplorer", shell=True)

    @classmethod
    def tearDownClass(cls):
        cls.stop_static_server()
        cls.webdriver.kill()
        super(SPAIntegrationTestCaseMixin, cls).tearDownClass()

    @classmethod
    def start_static_server(cls):
        with open('{}/divshot.log.txt'.format(cls.test_log_location), 'wb') as log_file:
            cls.static_server_process = subprocess.Popen(cls.static_server_command, shell=True,
                                                         stdout=log_file, preexec_fn=os.setsid)

    @classmethod
    def start_webdriver(cls):
        with open('{}/webdriver.log.txt'.format(cls.test_log_location), 'wb') as log_file:
            cls.webdriver = subprocess.Popen(['webdriver-manager', 'start'],
                                             stdout=log_file, stderr=log_file)

    @classmethod
    def poll_until_servers_up(cls):
        start = datetime.now()
        servers_up = {cls.live_server_url: False,
                      "http://localhost:4444/wd/hub": False}
        while (datetime.now() - start).seconds < POLLING_TIMEOUT:
            for url in servers_up:
                try:
                    resp = requests.get(url)
                except requests.ConnectionError:
                    time.sleep(POLLING_INTERVAL)
                else:
                    servers_up[url] = True
            if all([up for url, up in servers_up.items()]):
                return
        raise TimeoutException("The server(s) at {} didn't start within {} seconds".format(
            [url for url, up in servers_up.items() if not up], POLLING_TIMEOUT))

    @classmethod
    def stop_static_server(cls):
        os.killpg(cls.static_server_process.pid, signal.SIGTERM)

    def run_protractor(self):
        protractor_command = 'protractor {}'.format(self.protractor_conf)
        protractor_command += ' --baseUrl {}'.format(self.live_server_url)
        if self.specs:
            protractor_command += ' --specs {}'.format(','.join(self.specs))
        if self.suite:
            protractor_command += ' --suite {}'.format(self.suite)
        for key, value in self.get_protractor_params().items():
            protractor_command += ' --params.{key}={value}'.format(
                key=key, value=value
            )
        return_code = subprocess.call(protractor_command.split())
        self.assertEqual(return_code, 0)

    def run_protractor_with_specs(self, specs):
        if not isinstance(specs, list):
            specs = [specs]
        self.specs = specs
        self.run_protractor()

    def get_protractor_params(self):
        """A hook for adding params that protractor will receive."""
        return {
            'live_server_url': self.live_server_url
        }


def discover_protractor_dirs():
    return os.listdir('./{}'.format(BASE_TEST_DIR))


def get_test_methods(test_class):
    if not ELEMENT_EXPLORER:  # don't run tests if elementExplorer flag was passed
        dirs = discover_protractor_dirs()
        dirs_from_env = os.environ.get('TEST_SPEC_DIRS')  # comma separated list
        if dirs_from_env:
            dirs_from_env = dirs_from_env.replace(' ', '').split(',')
            for dir in dirs_from_env:
                if not dir in dirs:
                    raise Exception("Looks like you passed an invalid spec directory <{}>. "
                                    "The available options are {}".format(dir, dirs))
            print "Heads up: We're running only these specs (read from $TEST_SPEC_DIRS):"
            for dir in dirs_from_env:
                print "- ", dir
            dirs = dirs_from_env

        # Create one test method on the TestCase class for each directory of Protractor tests
        for dir in dirs:
            specs = ['{}{}/*.spec.js'.format(BASE_TEST_DIR, dir), ]
            def test_method(specs):
                return lambda self: self.run_protractor_with_specs(specs)
            setattr(test_class, 'test_{}'.format(dir), test_method(specs))
