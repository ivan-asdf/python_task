# Domain email/phone scraper

This project allows, given domain, to try to find email and phone associated with the domain.
It works on the principle of a "collector" which is a given method for retrieving said info.
As of right now there a 2 collectors:
* whois - for whois lookup
* scrape - for scraping website static pages

## Libraries/Technologies used

- Writen using `Django` web framework
- `Celery` for running async collector jobs as celery tasks
- `RabbitMQ` required for communication between `Django` - `Celery`
- `PostrgreSQL` as database
- `Docker` for managing services - All the previous listed services are setup and ran using docker-compose
- `GNU Makefile` for running specific docker-compose/migrations/cleanup commands
- Python library `beautifulsoup4` for parsing html
- Python library `python-whois` for whois requests
- Python library `watchdog` for runtime autoreload of code changes

##### Main models
- `Domain` represents domain added by user
- `Collector` represents predefined methods for aquiring data from domain(whois, scrape), can be enabled/disabled by user
- `CollectorJob` represents a celery task that runs a given `Collector` with given `Domain`. Used to track status of the task
- `Contact` represents a contact entry(phone/email) that is aquired from given `Domain` and `Collector`

# Features

- Adding domains with validation
- Collecting contact information from websites
- Managing collectors

## Setup & Run

### Dev
- The easiest way is to run `make db-clean-full` which will clean db(if exists), run migrations & start the services
- Alternatively you could do those seperately with `make run-dev` & `make migrate` (which will not clean db on rerun)

#### Note:
- In dev there is a default created user `asdf:asdf`
- In dev you can add already existing domains to rerun the same expected logic
  
### Prod
- Run `make run-prod` & `make migrate`

## Usage

**You can add domains in the "Add Site" page**
![image](https://github.com/ivan-asdf/python_task/assets/57415060/6ee5d0d4-1957-487a-90e5-f8d9258a6e69)
Once added by clicking "Add" button. The enabled collector will start running. As of right now there is no way to track their progress.

**After a while you could go to the "Contacts" page to view retrieved contact info of the added site and with which collector it was retrieved in the column "Source"**
![image](https://github.com/ivan-asdf/python_task/assets/57415060/7ff3a1e6-824b-4305-8133-601d6c438fe0)
Make sure to refresh page if you want to see contacts added as of now

**You can view  collectors in the "Collectors" page. You can enable/disable them with the buttons in the "Action" column**
![image](https://github.com/ivan-asdf/python_task/assets/57415060/f18bc15b-fa8d-415e-ac5a-84ae4bd54e1f)
A disabled collector will not run for newly added domains. **Disabling collector will NOT STOP already running collector jobs for already added domains.**
**Nor will enabling collector run a collector job on already added domains.**

#### Some test domains, their expected contact type retrieved & from which source
- speedy.bg
  - scrape
    - phone
- a1.bg
  - scrape
    - phone
    - email
- nikem-bg.net (slower)
  - whois
    - email
  - scrape
    - phone
- bulsatcom.bg
  - scrape
    - phone
    - email
- google.com
  - whois
    - email
  - scrape
    - email
- google.at
  - whois
    - phone
    - email
- google.co.cr
  - whois
    - phone
- druid.fi
  - scrape
    - phone
    - email



