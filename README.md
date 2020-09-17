# Notes App Capstone Project 

## To run this project

Clone this repo

Move to the folder  NotesApp-shriya

Create a virtual environment and activate it.
```bash
virtualenv venv
source venv/bin/activate
```

Install all dependencies

```bash
pip3 install -r requirements.txt
```

<hr>

### To create databse and tables

In *.env* file change the username and password to your postgres.

Then run the following commands:

```bash  
$ python3
$ from notes import db
$ db.create_all()
$ exit()
```
<hr>

### Now that the Database is set,

Run the following command:
```bash
python3 run.py
```

<hr>

### To delete the Database

```bash  
python3 drop_db.py 
```
