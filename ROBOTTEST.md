
# Instruction to run all tests using docker

This is the same way circle ci run the tests.
You can follow these instructions below to run it locally.

## Build docker image

Before you run any test, you need to build the base image first.

```
docker build --tag robot_tests -f Dockerfile-bootstrap .
```

Then this command below will run buildout and npm build inside docker image.
If the code changes you need to redo this step.

```
docker build --tag robot_tests .
```

There are two ways to run the tests:

1. using docker compose (recommended)
2. using docker directly

## 1. Using docker compose (recommended)

### Start selenium at background

Firstly, run selenium in the background using docker-compose

```
docker-compose -f docker-compose.test.yml -p grid up -d selenium
```

and then choose the few options below to run the tests.

### A. Run the all the tests (not working)

```
docker-compose -f docker-compose.test.yml -p grid run plominotest --rm -e bin/test --all
```

### B. Run a single test

```
docker-compose -f docker-compose.test.yml -p grid run --rm --name "plominotest" plominotest bin/test --all -t "Scenario I can add a validation rule to a field"
```

### C. Run the all the tests with output statement (not working)

if you are modifying tests and also want to see the test output

```
docker-compose -f docker-compose.test.yml -p grid run --rm --name "plominotest" -v $PWD/src/Products/CMFPlomino/tests/:/plone/instance/src/Products/CMFPlomino/tests -v $PWD/test:/plone/instance/parts/test  plominotest bin/test --all -t "Scenario I can add a validation rule to a field"
```

### D. Run using robot-server (faster to debug tests)

Firstly, you need start robot-server (this will take some time)

```
docker-compose -f docker-compose.test.yml -p grid up -d robot-server
```

#TODO should be able to use docker logs to see when its ready, or have some other test. ```docker-compose -f docker-compose.test.yml -p grid logs -f robot-server``` should work but doesn't

and then you got two options to run the tests:

i. run all robot tests

```
docker-compose -f docker-compose.test.yml -p grid up robot
```

ii. OR run a single robot test

```
docker-compose -f docker-compose.test.yml -p grid run robot bin/robot --outputdir=/buildout/parts/test --variable=REMOTE_URL:http://selenium:4444/wd/hub --variable=PLONE_URL:http://robot-server:55001/plone  -t "Scenario: I can add a new empty view from '+' button" /buildout/src/Products/CMFPlomino/tests/robot/test_views.robot
```





## 2. Using docker directly (equiv to above)

Start the selenium server

```
docker run --rm -d -p 4444:24444 -p 7777:25900 -p 55001:55001 -p8080:8080 -v /dev/shm:/dev/shm -v $PWD/src/Products/CMFPlomino/tests/:/buildout/src/Products/CMFPlomino/tests -v $PWD/test:/buildout/parts/test --privileged --rm --name rtests robot_tests
```

Start the test server and wait for it to start

```
docker exec -ti rtests /bin/bash -c "cd /buildout ;  bin/robot-server Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING"
```

In a new terminal window execute the tests:

```
docker exec -ti rtests /buildout/bin/robot --variable REMOTE_URL:http://127.0.0.1:24444/wd/hub --outputdir=/buildout/parts/test /buildout/src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot
```

If you mapped your local test dir you will see the output of the tests here

To shut down the server do

```
docker kill rtests
```

You can also run the non robot tests with

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/test"
```

or the full test suite with

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/test --all"
```

To interact with the robot-server use http://localhost:55001/plone

The robot-server tests users are 'test-user' or 'admin' with password of 'secret'

Another way to run the tests is using docker-compose, which will launch both selenium and pretaform togeather and then run
the tests. You can also look in .circleci/config.yml to see how that uses compose to run the tests

```
docker-compose -f docker-compose.test.yml up
```

To interact with the running application. Below you can start a server which is available on port 8080. user admin:admin.

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/instance fg"
```
