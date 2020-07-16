# Scheduler

Scheduler is a Flask web application designed to help teams schedule meetings.

## Usage

Scheduler allows users to register as members and create teams which creates a page for that team. Members can join teams that already exist if they know the password for that team. Once a team is created, any member of that team may make an 'availability request' on the team page which creates a page for that availability request. Members of a team can add 'availability slots' for an availability request which indicate when they are available for that request. This is done on the availability request page. If more than two members have responded to an availability request, the common times that everyone who has answered are available is desplayed on the availability request page. Any member may also create a 'booked date' to indicate that a time has been chosen for a particular availability request. Note that this may be done regardless of whether or not all members of a team have responded to an availability request. Also note that if an availability request is deleted it *does not* delete the booked date associated with it. 

Note that 'teams' are referred to as 'organizations' in the source code.