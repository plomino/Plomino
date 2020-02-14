# Plomino IDE

# Build

```
$ cd ./ide
$ npm install
$ npm i -g typescript@2.3.2
$ npm i -g typings@2.1.1
$ typings install
$ npm run build
```

you will also need a built plone to properly test the ide. ensure you have python 2.7 and prerequsites for http://pillow.readthedocs.io/en/3.1.x/installation.html

```
$ cd ..
$ virtualenv-2.7 .
$ bin/python bootstrap-buildout.py --setuptools-version=8.3
$ bin/buildout -N
```

You may also have to build the Plomino js using

```
./bin/plone-compile-resources --site-id=Plone --bundle=plomino
```
NB: if commiting this compiled version ensure you update src/Products/CMFPlomino/profiles/default/registry.xml with the compiled date and reinstall the plugin)

# Linting
In addition to the typescript compiler providing warnings and error checking, eslint provides additional code checks. To use the linter, run:

```
$ npm run lint
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

# Build from the latest code

If you are not at 'ide' folder
$ cd ./ide


$ git pull origin advanced_ide
$ typings install
$ npm run build

# Release

To build a production release of the IDE, run ```npm run build``` and commit any changes in the ```../src/Products/CMFPlomino/browser/static/ide``` directory.
