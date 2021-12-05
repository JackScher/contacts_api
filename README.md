# contacts_api

requirements:
1. installed python, pip;
2. installed postgreql

to create virtual enviroment input into terminal:
1. mkdir "dir_name";
2. cd "dir_name";
3. python -m venv "./env";
4. source env/bin/activate;
5. pip install -r requirements.txt

instruction to create tables:
1. create database in postgresql;
2. in app.py set app.config['SQLALCHEMY_DATABASE_URI'] to 'postgresql://db_owner:db_owner_password@host/db_name';
3. activate virtual enviroment (command "source env/bin/activate");
4. input into terminal > python > from app import db > db.create_all() > exit()
