# ∫_test_

## Integration tests for Premiere and frontend SPAs using Protractor and Django.

### Quick start:

#### Set up:
- install protractor with `npm install protractor` (or better yet, add it to your SPA's `package.json`)
- `webdriver-manager update --standalone`
- `export PREMIERE_ROOT=<root_dir_of_Premiere_install>`
- `export SUMMA_TEST_ROOT=<root_dir_of_this_install>`
- `export PYTHONPATH=<root_dir_of_SPA_repo>:$SUMMA_TEST_ROOT:$PREMIERE_ROOT:$PREMIERE_ROOT/premiere`
- `export STATIC_SERVER_PORT=8082`
- place Protractor tests in subdirectories of `<root_dir_of_SPA_repo>/testing`
- write a `test_ui.py` file 
- Activate your Premiere virtualenv (you need all those dependencies to run the API server).

#### Run tests:
- `$SUMMA_TEST_ROOT/test.sh`

### How it works:
- The test loader looks for test directories in `<root_dir_of_SPA_repo>/testing`, expecting something like:
```
- root
  - testing <- this directory must be called "testing"
    - test-blergs-can-moog
      - testathing.spec.js
      - testanotherthing.spec.js
    - test-blergs-have-farks
      - onemoretest.spec.js
    - test_ui.py
```
- Each directory will be run as a test method on a test class that you'll need to define in `test_ui.py` (more details below).  What that means is that the database will be rolled back to a clean state for each directory.  E.g.: 
  1. Start tests, create empty database
  2. Database gets filled with some test data by your setUpClass method in test_ui.py (let's call this "State A")
  3. Run `testathing.spec.js`
  4. Run `testanotherthing.spec.js`
  5. Roll database back to state A
  6. Run `onemoretest.spec.js`

- What's this test_ui.py stuff about?  It's a python file declaring a TestCase class and then running `get_test_methods(...)` to add a test method for each protractor test directory.  It should be a set-it-and-forget-it kind of thing.  You'll probably want to use the `setUpClass` method to put some data in the database, and the `get_protractor_params` method to pass data to [protractor params](https://github.com/angular/protractor/blob/master/docs/referenceConf.js#L233-L243) (things you created in the database that you need the client-side tests to know about, like user login info and project-specific data).  Here's an example:
```python
# test_ui.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from integration_tests import SPAIntegrationTestCaseMixin, get_test_methods


class ProtractorTests(SPAIntegrationTestCaseMixin, StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        """Set up, run once for all methods on this class"""
        put_some_data_in_the_database()
        other_test_setup()
        super(ProtractorTests, cls).setUpClass()

    def get_protractor_params(self):
        """A hook for adding params that protractor will receive."""
        params = super(ProtractorTests, self).get_protractor_params()
        params.update({
            'user1username': "alice",
            'user2username': "bob",
            'user1password': "pass1",
            'user2password': "pass2",
        })
        return params


get_test_methods(ProtractorTests)

```

#### Options


##### --specs
Like the `--specs` argument passed to Protractor when Protractor is called directly, in order to run only some Protractor specs, set the environment variable TEST_SPEC_DIRS to a comma-separated list of directories.  E.g. 
  - `export TEST_SPEC_DIRS=test-blergs-can-moog` or
  - `export TEST_SPEC_DIRS=test-blergs-can-moog,test-blergs-have-farks`

##### --elementExplorer
to run Protractor's Element Explorer, use `$SUMMA_TEST_ROOT/test.sh --elementExplorer`

### Continuous Integration with CircleCI

Check out [OverDrive's circle.yml](https://github.com/MobileWorks/overdrive/blob/master/circle.yml).  Particularly:
- `git clone --depth 1 https://github.com/MobileWorks/summa-test.git $SUMMA_TEST_ROOT`
- `$SUMMA_TEST_ROOT/install_premiere.sh`
