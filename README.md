# Data Modelling with Relational Databases
This project contains a database that simplifies the querying of data on songs and user activity for the sparkify analytics team.


### DB Schema
The DB Schema used for this project is the star schema. 
It consists of one Fact table (song_play) and four Dimension Tables (users, songs artists and time). 
This schema design helps with simplifying complex queries and allows for greater performance when reading data from the database.


### Project Structure
sql_queries.py
Contains the drop, creation and insertion statements from given datasets and a select query that gets the songid and artistid. 

create_tables.py
Contains the methods that execute the drop and create table queries found in the sql_queries file .

etl.py
Extracts data from files and loads it into sparkifydb

## Usage
### Requirements
```
Python 3
Postgresql
```
run the following command:
```
python create_tables.py
```
To run the ETL pipeline:
```
python etl.py
```

### Example Query
This query selects all songs with a title containing the word "World"
 ```
select *
from songs
where title like '%World%```