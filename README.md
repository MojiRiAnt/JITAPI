# JITAPI
Junior Informatics Tournament Project

### TODO

* New tokens and secrets generation (nothing implemented yet).
* A 'routes' module handling queries.

### How to import and run our project

Using our installation script:
```console
$ cd ~/Downloads  # navigate to your Downloads directory
$ wget https://raw.githubusercontent.com/MojiRiAnt/JITAPI/master/ImportJITAPI.sh
 # download our installation script
$ cd ~/your/import/directory  # navigate to where you want
$ bash ~/Downloads/ImportJITAPI.sh  # execute the script
```
Other useful commands:
```console
$ source ~/your/import/directory/JITENV/bin/activate  # activate our environment
$ python3 ~/your/import/directory/JITENV/JITAPI/main.py  # run our project
```

### Project structure

* main.py -- the main module
* database.py -- database handling
* crypto.py -- additional crypto functions
* routes.py -- queries handling
