# e2e-pytest-poc
Example of machine-api-operator e2e tests in Python/pytest.

There are fixtures to create machineSet before test and delete it after each test.
There are no actual tests implemented, since this is just demo to show how it would work.  

Pytest will look for kubeconfig same as `oc` tool. 

`make venv` to setup virtual environment. 
`make e2e` to run example test on cluster. 

`make e2e-one` to run just one test. `-k` flag s used to run test by name.

`pytest -v -s` to show stdout 
