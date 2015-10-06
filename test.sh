if [ -z $PREMIERE_ROOT ]; then
	echo "Error: you must set environment variable PREMIERE_ROOT to the root directory of your Premiere install."
fi

# janky way to pass elementExplorer flag to test runner
if [ "$1" == "--elementExplorer" ]; then
	export ELEMENT_EXPLORER=1
fi

if [ -z $STATIC_SERVER_LOG_LOCATION ]; then
	export STATIC_SERVER_LOG_LOCATION=.logs/testing
fi
mkdir -p $STATIC_SERVER_LOG_LOCATION

# configure API server, run tests
source $PREMIERE_ROOT/premiere/settings/utils/local_env_postactivate.sh
# use real leadcloud
export LEAD_CLOUD_URL=http://lead-cloud-staging.leadgenius.com/
$PREMIERE_ROOT/premiere/manage.py test tests.test_ui --settings=integration_test_settings --nomigrations --noinput --verbosity 0
exit_code=$?

# give an informative exit code for CircleCI
exit $exit_code
