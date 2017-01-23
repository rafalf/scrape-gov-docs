## Setting up:

* install Python 2.7.12 ( or newer e.g. 2.7.13 ) - https://www.python.org/downloads/release/python-2712/
* WINDOWS: run command line as Administrator and type in : ```pip``` to make sure is installed
if you get an error while running ```pip```, in command line you need to go to C:\Python27\Scripts to install 
the following packadges, otherwise you should be able to run it from any directory in the command line. Make sure the command line is started as Administrator
* win: ```pip install lxml==3.6.0```  (other e.g. Mac ```pip install lxml```)
* ```pip install requests```
* ```pip install```
* ```pip install beautifulsoup4```

## Running:
* ``` python run_scraper.py --files update ```  - to check and update documents
* ``` python run_scraper.py --files gov-urls``` - to pull down all documents
