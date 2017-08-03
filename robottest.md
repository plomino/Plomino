Edit src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot. and add the following variable below the ${BROWSER} entry:

```
${REMOTE_URL}  http://127.0.0.1:24444/wd/hub
```


Build the image. You will need to repeat after each git pull.

```
docker build --tag robot_tests .
```

Start the selenium server

```
docker run -d -p 4444:24444 -p 7777:25900 -v /dev/shm:/dev/shm -v ./PlominoWorkflow/src/Products/CMFPlomino/tests/:/buildout/src/Products/CMFPlomino/tests --privileged --rm --name rtests robot_tests
```

Start the test server

```
docker exec -ti rtests /bin/bash -c "cd /buildout ; bin/robot-server --reload-path src Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING &"
```

Execute the tests:

```
docker exec -ti rtests /bin/bash -c "cd /buildout; bin/robot src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot"
```
