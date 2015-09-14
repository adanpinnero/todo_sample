# Todo Project
This is the third project of the Udacity Fullstack Nanodegree.
It's a simple app that allows users to add Projects and Tasks within them.

## Pre-Requisites
**Python 2** and **Sqlite**.

## Setup 
You can run the **provision_db.py** file to have an example project created.
This is not mandatory however. You can simply run the **application.py**
and open your browser on localhost:5000.

## Usage
You need to log in with a Googlemail account. This will allow you to create Projects and Tasks.

## Limitations
The following are steps that should be taken to improve the app:
- Error handling of form data (WTForms)
- Ability to "check" tasks, rather than deleting them (-> Ajax calls)
- Tasks within a project are not deleted when the Project is deleted
- The design is very basic
- Postgresql would be a more serious db choice

## Resources
Bootstrap (Dashboard example) was used to help with the styling of the app.
jQuery is used as part of Bootstrap for the flash messages.