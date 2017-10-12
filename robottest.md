
Build the base image first. 
```
docker build --tag robot_tests -f Dockerfile-bootstrap .
```

Then build buildout and npm build. If the code changes you need to redo this step.

```
docker build --tag robot_tests .
```

# Using docker-compose


Run docker hub in the background


```
docker-compose -f docker-compose.test.yml up -d hub chrome
```


```
docker-compose -f docker-compose.test.yml run plominotest -e bin/test --all
```

Run a test

```
docker-compose -f docker-compose.test.yml run --name "plominotest" plominotest bin/test --all -t "Scenario I can add a validation rule to a field"
```

if you are modifying tests and also want to see the test output

```
docker-compose -f docker-compose.test.yml run --name "plominotest" -v ./src/Products/CMFPlomino/tests/:/buildout/src/Products/CMFPlomino/tests -v ./test:/buildout/parts/test  plominotest bin/test --all -t "Scenario I can add a validation rule to a field"
```

OR you can use robot directly. First start robot-server

```
docker-compose -f docker-compose.test.yml up -d hub chrome robot-server
```

followed by a test run

```
docker-compose -f docker-compose.test.yml up robot
```

or just to run a single test

```
docker-compose -f docker-compose.test.yml run robot bin/robot --outputdir=/buildout/parts/test --variable=REMOTE_URL:http://hub:4444/wd/hub --variable=PLONE_URL:http://robot-server:55001/plone  -t "Scenario: I can add a new empty view from '+' button" /buildout/src/Products/CMFPlomino/tests/robot/test_*.robot
```

# Using docker


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

