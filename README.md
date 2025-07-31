# University Research Insights (URI)
>**Discover your best fit**
## Purpose
The University Research Insights (URI) application is designed to allow users to explore and compare research profiles and performance of universities based on faculty research and publications. Our target users include prospective graduate students who are looking to identify top institutions based on their research interests, policymakers and academic evaluators who are benchmarking institutions for national rankings, accreditation, or funding initiatives, and faculty members who are looking to find potential collaborators for research projects based on universities with more faculty who overlap with their research domain and expertise. Our objectives are to compare and benchmark universities by research impact, visualize university research trends over time, and identify the top-cited researchers within each university.
## Demo 
Our demo video can be found [here](google.com).
## Installation 
### First, clone our repository  
`git clone https://github.com/CS411DSO-SU25/Edward_Nikki.git`  
### Second, create a virtual environment and install the required packages
```
conda create -n cs411_final_project python=3.11
conda activate cs411_final_project
pip install -r requirements.txt
```
### Third, create a .env file in the project directory and fill it out as follows with your db specifications
```
# .env

DB_NAME=academicworld
DB_HOST=localhost

# MySQL Database Configuration

MYSQL_DB_PORT=3306
MYSQL_DB_USER=<YOUR_MYSQL_DB_USER>
MYSQL_DB_PASSWORD=<YOUR_MYSQL_DB_PASSWORD>

# Neo4j Database Configuration

NEO4J_DB_PORT=7687
NEO4J_DB_USER=<YOUR_NEO4J_DB_USER>
NEO4J_DB_PASSWORD=<YOUR_NEO4J_DB_PASSWORD>

# Mongo Database Configuration
MONGO_PORT=27017
```
### Last, move into the `src` folder and execute the code  
`cd src/`  

`python app.py`
> [!NOTE]
> Make sure the neo4j DBMS is started when you run the application.
## Usage
Our application has 7 main functions. Instructions on how to use each one are described below.
### Faculty Citation Rankings by University
This widget allows the user to select one university from the dropdown and view the top 10 faculty by their total number of citations on their publications. The pie chart shows each faculty member's share of their total citations among the top 10 at that university. This allows the user to view the faculty that have the highest research influence based on citation count and understand the magnitude of their influence. `American University` is the university that is preselected.
### University Publications Over Time
This widget allows the user to select one or multiple universities from the dropdown, select a time range through the year range slider, and view how many publications each university published during that time frame. The user is able to visualize how the number of publications at each selected university changes over time and compare the number of publications across each selected university. This allows the user to understand trends in research output for each selected university.
### Top Universities by Faculty Keyword Score
This widget allows the user to select one or multiple keywords and view the top universities based on the combined score of the faculty who are associated with those keywords.
### Top Universities by Publication Keyword-Relevant Citation Score
This widget allows the user to select one keyword and view the top 10 universities based on the combined publication keyword-relevant citation score (KRC) for that keyword. `20th century` is the keyword that is preselected.
### Add University
This widget allows the user to add a new university. The add widget contains a form for entering information about a new university. Clicking the `Add` button inserts the university information into the university table in the academicworld MySQL database and the university id automaticaly increments by the `max university id + 1`. The user is required to add the university name and can optionally add a photo url of the university logo. The university name was given a unique constraint meaning that if a user tries to add a university name that already exists, they would be notified that the university name already exists and is thus not added to the university table.
### Delete University
This widget allows the user to delete a university. The delete widget contains a dropdown of universities currently in the university table and the user can select one university to delete. Clicking the `Delete` button deletes the university name and the corresponding entire tuple associated with the university name. The delete widget dynamically reflects all of the university names at a given time even after a new university name is inserted into the university table in the academicworld MySQL database.
### Update publications
This widget contains a series of dropdowns so that the user can select a specific university, faculty member, and their publications. It allows the user to add, update, or delete publications for that faculty member. The `Add` and `Update` buttons open modals with forms for the user to fill out or modify the necessary information in the given fields. Clicking the `Add`, `Update`, or `Delete` buttons will update the publication and faculty_publication table in the academicworld MySQL database accordingly.
## Design
Our application uses the dash framework from `Plotly` to implement our dashboard. We've designed the dashboard using `html`, `dash bootstrap components`, and `Plotly Express`. The dashboard uses a simple color scheme revolving around different shades of blue, includes a title at the top along with the UIUC logo, and places each widget into its own widget card allowing the user to easily distinguish between each widget. Each component is laid out in rows with 2 widgets per row and the widget card background colors are color coded so that the sky blue widgets correspond to widgets relating to keyword scores, the gray widgets correspond to widgets related to Insert/Update/Delete operations, and the navy blue widgets correspond to widgets that are not related to the previous two widget types.
## Implementation
All of our code is written in Python. There are database util files in the [`utils`](https://github.com/CS411DSO-SU25/Edward_Nikki/tree/main/src/utils) folder to connect to our databases and to implement our widget queries for each type of database. The name of each Python file in the [`utils`](https://github.com/CS411DSO-SU25/Edward_Nikki/tree/main/src/utils) folder corresponds to the type of database we are querying from (i.e. [`mysql_utils.py`](https://github.com/CS411DSO-SU25/Edward_Nikki/blob/main/src/utils/mysql_utils.py) includes all operations on the academicworld MySQL database). The top left widget, middle left widget, bottom left 1 widget, bottom left 2 widget, and bottom right widget queries from the academicworld database in MySQL. The top right widget queries from the academicworld database in MongoDB. The middle right widget queries from the academicworld database in Neo4j. We've used `mysql.connector` Python library to connect to the academicworld database in MySQL, `pymongo` Python library to connect to the academicworld database in MongoDB, and `neo4j` Python library to connect to the academicworld database in Neo4j. Additionally, there are a series of callback methods in our `app.py` file that call the query methods in order to connect them to our app. There is also a series of methods that set and use the callback methods to create dropdowns, inputs, and charts to create each widget. These methods are then injected into our html layout. Lastly we've used the `dotenv` Python library to help us define a `.env` file to store our user specific database configuration files.
## Database Techniques
We have implemented 5 database techniques.
### Indexes
We created indexes in our `mysql_utils.py` file and the `mongodb_utils.py` file in order to decrease the latency of our queries. Specifically, in `mysql_utils.py`, indexes were created on `faculty_keyword(faculty_id)`, `faculty_keyword(keyword_id)`, `faculty(university_id)`, and `keyword(name)` to speed up the join operations performed between these tables. In `mongodb_utils.py`, an index was created on `publications.id` to speed up the join operation performed between the `faculty` collection and the `publications` collection.
### Trigger
A trigger is implemented in our `mysql_utils.py` file so that we ensure the removal of both the `publication` entry and `faculty_publication` entry when a publication is deleted.
### View
A view is implemented in our `mysql_utils.py` file in order to simplify the queries for our middle left widget. It aggregates the total faculty keyword scores for each university allowing the middle left widget to simply query from this view rather than having to recompute the total faculty keyword scores each time.
### Transaction
We've implemented transactions in our `mysql_utils.py` for adding a university (bottom left widget 1) and deleting a university (bottom left widget 2) to ensure that a university is safely inserted or deleted and if a new university fails to be inserted or deleted, the transaction is rolled back and the database is returned to its state before the transaction began. Additionally, transactions are implemented for retrieving faculty citation rankings by university (top left widget) and updating publications (bottom right widget).
### Constraint
A unique constraint on university name is implemented in our `mysql_utils.py` file by altering the schema of the university table in the academicworld MySQL database to ensure that there can not be duplicate university names.
## Contributions
### Nikki
| Item      | Time Spent (hours) |
| :---------------------------------------- | :-----------  |
| Created repo and initialized app | 2 |
| Connected the databases to the application | 1 |
| Wrote the Faculty Citation Rankings by University widget and its corresponding queries | 3 |
| Wrote the Top Universities by Publication KRC widget and its corresponding queries | 3 |
| Wrote the Update Publications widget and its corresponding queries | 5 |
| Drafted this documentation | 2 |
| ***Total*** | ***16*** |
### Edward
| Item      | Time Spent (hours) |
| :---------------------------------------- | :-----------  |
| Created an outline of our dashboard through selecting a topic, brainstorming ideas we wanted to analyze, and architecting widgets supporting our analysis | 3 |
| Designed the overall html layout of the dashboard and color scheme | 4 |
| Wrote the University Publications Over Time and corresponding queries (top right widget) | 3 |
| Wrote the Top Universities by Faculty Keyword Score and corresponding queries (middle left widget) | 5 |
| Wrote the Add University and Delete University widgets and corresponding queries (bottom left widgets) | 5 |
| Edited and added numerous details to the documentation | 2 |
| ***Total*** | ***22*** |
