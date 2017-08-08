
Build the base image. You only need to do this if there is a big change to the buildout

```
docker build --tag robot_tests -f Dockerfile-bootstrap .
```

Subsequent builds you can do

```
docker build --tag robot_tests .
```

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



To interact with the running application. Below you can start a server which is available on port 8080. user admin:admin.

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/instance fg"
```

