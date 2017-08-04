Edit src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot. and add the following variable below the ${BROWSER} entry:

```
${REMOTE_URL}  http://127.0.0.1:24444/wd/hub
```


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
docker run -d -p 4444:24444 -p 7777:25900 -v /dev/shm:/dev/shm -v $PWD/src/Products/CMFPlomino/tests/:/buildout/src/Products/CMFPlomino/tests --privileged --rm --name rtests robot_tests
```

Start the test server and wait for it to start

```
docker exec -ti rtests /bin/bash -c "cd /buildout ; bin/robot-server --reload-path src Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING" 
```

In a new terminal window execute the tests:

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/robot src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot"
```

To shut down the server do

```
docker kill rtests
```
