import os
import signal
import subprocess
import sys

from protractor.test import ProtractorTestCaseMixin


ELEMENT_EXPLORER = False
if os.environ.get("ELEMENT_EXPLORER"):
    ELEMENT_EXPLORER = True
    del os.environ['ELEMENT_EXPLORER']


class SPAIntegrationTestCaseMixin(ProtractorTestCaseMixin):
    specs = None  # set on each test method
    protractor_conf = 'tests/conf.js'
    live_server_url = 'http://localhost:{}/'.format(os.environ.get('STATIC_SERVER_PORT'))
    static_server_command = 'divshot s -p $STATIC_SERVER_PORT'

    @classmethod
    def setUpClass(cls):
        """If you want to have access to objects you've created in the database in your setUpClass
        method on your subclass when using elementExplorer, call
        super(YourTests, cls).setUpClass() **at the end** of your setUpClass method instead of at
        the beginning."""
        super(SPAIntegrationTestCaseMixin, cls).setUpClass()
        cls.start_static_server()

        # optionally run elementExplorer
        if ELEMENT_EXPLORER:
            print "Pausing for element explorer... "
            subprocess.call("protractor --elementExplorer", shell=True)


    @classmethod
    def tearDownClass(cls):
        super(SPAIntegrationTestCaseMixin, cls).tearDownClass()
        cls.stop_static_server()

    @classmethod
    def start_static_server(cls):
        log_file = open('{}/divshot.log.txt'.format(os.environ.get('STATIC_SERVER_LOG_LOCATION')), 'w')
        cls.static_server_process = subprocess.Popen(cls.static_server_command, shell=True, stdout=log_file, preexec_fn=os.setsid)

    @classmethod
    def stop_static_server(cls):
        os.killpg(cls.static_server_process.pid, signal.SIGTERM)

    def test_run(self):
        # override default test method, kinda janky.  needed because python picks up every method
        # named test_<foo> as a test case.
        pass

    def run_protractor(self):
        # copy of self.test_run
        # copied from https://github.com/jpulec/django-protractor/blob/master/protractor/test.py
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


def discover_protractor_dirs():
    return os.listdir('./tests/e2e/')


def get_test_methods(test_class):
    if not ELEMENT_EXPLORER:
        dirs = discover_protractor_dirs()
        dirs_from_env = os.environ.get('TEST_SPEC_DIRS')  # comma separated list
        if dirs_from_env:
            dirs_from_env = dirs_from_env.replace(' ', '').split(',')
            for dir in dirs_from_env:
                 if not dir in dirs:
                     raise Exception("Looks like you passed an invalid spec directory <{}>.  The available options are {}".format(dir, dirs))
            print "Heads up: We're running only these specs (read from $TEST_SPEC_DIRS):"
            for dir in dirs_from_env:
                print "- ", dir
            dirs = dirs_from_env

        # Create one test method on the TestCase class for each directory of Protractor tests
        for dir in dirs:
            specs = ['tests/e2e/{}/*.spec.js'.format(dir), ]
            def test_method(specs):
                return lambda self: self.run_protractor_with_specs(specs)
            setattr(test_class, 'test_{}'.format(dir), test_method(specs))