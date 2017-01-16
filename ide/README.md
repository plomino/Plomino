# Plomino IDE

# Build

```
$ cd ./ide
$ npm install
$ npm run build
```

# you will also need a built plone to properly test the ide

```
$ cd ..
$ virtualenv .
$ bin/python bootstrap-buildout.py --setuptools-version=8.3
$ bin/buildout -N
```



# Run

```
$ bin/instance fg
```

1. Go to http://localhost:8080
2. Add a plone site (default user is admin:admin)
3. Go to ```site setup > addons```
4. find  ```Products.CMFPlomino``` and click ```activate```
5. Go to home
6. ```Add new > PlominoDatabase```. Give it a name
7. Click IDE. (also can go to: /path/to/plomino/database/++resource++Products.CMFPlomino/ide/index.html)

Further npm rebuilds don't require a plone restart so you can use ```npm run watch``` during development

# Release

To build a production release of the IDE, run ```npm run build``` and commit any changes in the ```../src/Products/CMFPlomino/browser/static/ide``` directory.
