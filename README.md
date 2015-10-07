# ∫_test_

## Integration tests for Premiere and frontend SPAs

### To run tests:
- `export PREMIERE_ROOT=<root_dir_of_Premiere_install>`
- `export SUMMA_TEST_ROOT=<root_dir_of_this_install>`
- `export PYTHONPATH=<root_dir_of_SPA_repo>:$SUMMA_TEST_ROOT:$PREMIERE_ROOT:$PREMIERE_ROOT/premiere`
- Activate your Premiere virtualenv (you need all those dependencies to run the API server).
- `export STATIC_SERVER_PORT=8082`
- `$SUMMA_TEST_ROOT/test.sh`