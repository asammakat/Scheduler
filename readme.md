# Scheduler

Scheduler is a Flask web application designed to help teams schedule meetings.

## Installation

To run on your local machine clone the [Scheduler repository](http://github.com/asammakat/Scheduler) and install the dependencies into your local environment. From Scheduler/ run:

```bash
export FLASK_APP=schedulerApp
export FLASK_ENV=development
```

Initialize the database with:

```bash
flask init-db
```

If you get the message 'Initialized the database.' you are ready to run Scheduler on localhost:5000/ with: 

```bash
flask run
```

## Usage

Scheduler allows users to register as members and create teams which creates a page for that team. Members can join teams that already exist if they know the password for that team. Once a team is created, any member of that team may make an 'availability request' on the team page which creates a page for that availability request. Members of a team can add 'availability slots' for an availability request which indicate when they are available for that request. This is done on the availability request page. If more than two members have responded to an availability request, the common times that everyone who has answered are available is desplayed on the availability request page. Any member may also create a 'booked date' to indicate that a time has been chosen for a particular availability request. Note that this may be done regardless of whether or not all members of a team have responded to an availability request. Also note that if an availability request is deleted it *does not* delete the booked date associated with it. 

Note that 'teams' are referred to as 'organizations' in the source code.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)