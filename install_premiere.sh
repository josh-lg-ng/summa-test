# http://stackoverflow.com/questions/821396/aborting-a-shell-script-if-any-command-returns-a-non-zero-value
set -e

# default to master, unless set by build parameters
# https://circleci.com/docs/parameterized-builds
if [ -z $PREMIERE_BRANCH ]; then
	export PREMIERE_BRANCH=master
fi

echo "Installing Premiere branch '$PREMIERE_BRANCH'..."
git clone --depth=1 --branch $PREMIERE_BRANCH https://github.com/MobileWorks/Premiere.git $PREMIERE_ROOT
pip install -r $PREMIERE_ROOT/requirements.txt
pip install -r $PREMIERE_ROOT/requirements-dev.txt
psql -c "CREATE EXTENSION IF NOT EXISTS hstore;" -d template1