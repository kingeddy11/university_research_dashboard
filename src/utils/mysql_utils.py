import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


## MySQL connection setup
host = "localhost"
port = os.getenv("MYSQL_DB_PORT")
user = os.getenv("MYSQL_DB_USER")
password = os.getenv("MYSQL_DB_PASSWORD")
database = "academicworld"

def get_connection():
    """
    Establishes a connection to the MySQL database.
    """

    return mysql.connector.connect(
        host = host,
        port = port,
        user = user,
        password = password,
        database = database
    )


## Middle Right Widget (top 10 universities by keyword score)
# Create index on faculty_keyword(faculty_id), faculty_keyword(keyword_id), faculty(university_id), and keyword(name)
index_queries = [
    "CREATE INDEX idx_faculty_keyword_faculty_id ON faculty_keyword(faculty_id)",
    "CREATE INDEX idx_faculty_keyword_keyword_id ON faculty_keyword(keyword_id)",
    "CREATE INDEX idx_faculty_university_id ON faculty(university_id)",
    "CREATE INDEX idx_keyword_name ON keyword(name)"
]

for query in index_queries:
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute(query)
        mysql_conn.commit()
        mysql_cursor.close()
        mysql_conn.close()
    except mysql.connector.errors.DatabaseError:
        pass  # if index already exists, ignore the error

# --- Add this block for the trigger ---
trigger_query = """
CREATE TRIGGER IF NOT EXISTS delete_faculty_publication_after_publication_delete
AFTER DELETE ON faculty_publication
FOR EACH ROW
BEGIN
    DELETE FROM publication WHERE id = OLD.publication_id;
END
"""

try:
    mysql_conn = get_connection()
    mysql_cursor = mysql_conn.cursor()
    # MySQL does not support IF NOT EXISTS for triggers, so catch error if it already exists
    mysql_cursor.execute("DROP TRIGGER IF EXISTS delete_faculty_publication_after_publication_delete")
    mysql_cursor.execute(trigger_query)
    mysql_conn.commit()
    mysql_cursor.close()
    mysql_conn.close()
except mysql.connector.Error as e:
    print("Error creating trigger:", e)
# --- End trigger block ---

# Function to validate keywords that exist in the keyword table
def validate_keywords(keywords):
    """
    Return a list of valid keywords that exist in the keyword table.

    Parameters
    ----------
    keywords: list of str
        List of keywords to validate.

    Returns
    -------
    list of str
    """

    if not keywords:
        return []
    
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        lowercase_keywords = [keyword.lower() for keyword in keywords]
        placeholders = ", ".join(["%s"] * len(lowercase_keywords))
        query = f"SELECT name FROM keyword WHERE LOWER(name) IN ({placeholders})"
        mysql_cursor.execute(query, lowercase_keywords)
        results = [row[0] for row in mysql_cursor.fetchall()]   
        mysql_cursor.close()
        mysql_conn.close()
        return results

    except mysql.connector.Error as e:
        print(f"Error validating keywords: {e}")
        return []

# Function to query top 10 universities by keyword score
def middle_left_query(keywords = None):
    """
    Query to get the top 10 universities by keyword score for filtered keywords.

    Parameters
    ----------
    keywords: list, optional
        List of keywords to filter by.

    Returns
    -------
    list
        A list of tuples containing university name and total keyword score.
    """

    try:
        # Validate keywords
        valid_keywords = validate_keywords(keywords) if keywords else []
        if keywords and not valid_keywords:
            return [("No matching keywords found", 0)]

        # Create a view for university keyword scores
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        create_view_query = "CREATE OR REPLACE VIEW university_keyword_score AS \
                            SELECT u.id as university_id, \
                                u.name as university_name, \
                                k.id as keyword_id, \
                                k.name as keyword_name, \
                                SUM(fk.score) AS total_keyword_score \
                            FROM faculty f \
                            JOIN faculty_keyword fk on f.id = fk.faculty_id \
                            JOIN keyword k ON fk.keyword_id = k.id \
                            JOIN university u on f.university_id = u.id \
                            GROUP BY u.id, u.name, k.id, k.name" 
        mysql_cursor.execute(create_view_query)

        # Query by keywords provided
        if keywords:
            placeholders = ", ".join(["%s"] * len(valid_keywords))
            query = f"SELECT university_name, total_keyword_score \
                    FROM university_keyword_score \
                    WHERE LOWER(keyword_name) IN ({placeholders}) \
                    ORDER BY total_keyword_score DESC \
                    LIMIT 10"
            mysql_cursor.execute(query, valid_keywords)
        else:
            mysql_cursor.execute("SELECT university_name, total_keyword_score \
                                FROM university_keyword_score \
                                ORDER BY total_keyword_score DESC \
                                LIMIT 10")
        
        results = mysql_cursor.fetchall()
        mysql_cursor.close()
        mysql_conn.close()

        return results

    except mysql.connector.Error as e:
        print(f"Error querying top universities by keyword score: {e}")
        return [("Query failed", 0)]
    
# Function to get all keywords to create dropdown options for the middle left widget
def get_all_keywords():
    """
    Returns a list of all keywords for dropdown options.
    """

    mysql_conn = get_connection()
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute("SELECT DISTINCT LOWER(k.name) FROM keyword k JOIN faculty_keyword fk ON k.id = fk.keyword_id JOIN faculty f ON fk.faculty_id = f.id JOIN university u ON f.university_id = u.id ORDER BY LOWER(k.name)")
    results = [row[0] for row in mysql_cursor.fetchall()]
    mysql_cursor.close()
    mysql_conn.close()
    return results

# Function for keyword suggestions with search term appearing at the start followed by other matches
def search_keywords_by_prefix(search_term):
    """
    Returns a list of keyword suggestions that start with the given search term
    followed by other matches.
    Parameters
    ----------
    search_term : str
        The term to search for in keywords.
    
    Returns
    -------
    list
        A list of keyword suggestions.
    """

    if not search_term:
        return []
    
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        # Keywords that start with the search term
        mysql_cursor.execute("""
            SELECT name FROM keyword
            WHERE LOWER(name) LIKE %s
            ORDER BY name
            LIMIT 10
        """, (search_term.lower() + "%",))
        prefix_matches = [row[0] for row in mysql_cursor.fetchall()]

        # Keywords that contain the term elsewhere
        mysql_cursor.execute("""
            SELECT name FROM keyword
            WHERE LOWER(name) LIKE %s AND LOWER(name) NOT LIKE %s
            ORDER BY name
            LIMIT 10
        """, ("%" + search_term.lower() + "%", search_term.lower() + "%"))
        contains_matches = [row[0] for row in mysql_cursor.fetchall()]

        mysql_cursor.close()
        mysql_conn.close()

        return prefix_matches + contains_matches
    except mysql.connector.Error as err:
        print(f"Error fetching keyword suggestions: {err}")
        return []


## Bottom Left Widget 1 (inserting into university table)
# set name to not null and unique
def alter_university_table():
    """
    Alters the university table to set name to not null and unique.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("ALTER TABLE university MODIFY name VARCHAR(255) NOT NULL UNIQUE")
        mysql_conn.commit()
        mysql_cursor.close()
        mysql_conn.close()
        print("University name column set to NOT NULL UNIQUE")
    except mysql.connector.Error as e:
        print("ALTER TABLE failed or already set name to not null and unique:", e)
    finally:
        mysql_cursor.close()
        mysql_conn.close()

# Function for inserting a new university
def insert_university(name, photo_url = None):
    """
    Inserts a new university into the university table.

    Parameters
    ----------
    name : str
        The name of the university.
    photo_url : str
        The URL of the university's photo.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        # Start transaction
        mysql_conn.start_transaction()

        # Get next available id
        mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM university")
        next_id = mysql_cursor.fetchone()[0]
        
        # Insert new university
        mysql_cursor.execute("""INSERT INTO university (id, name, photo_url) VALUES (%s, %s, %s)""", (next_id, name, photo_url))
        mysql_conn.commit()
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error inserting university:", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()


## Bottom Left Widget 2 (deleting from university table)
# Function for deleting an existing university
def delete_university(name):
    """
    Deletes an existing university from the university table.
    
    Parameters
    ----------
    name: str
        The name of the university to delete.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        # Start transaction
        mysql_conn.start_transaction()

        # Delete university by name
        mysql_cursor.execute("""DELETE FROM university WHERE name = %s""", (name, ))
        mysql_conn.commit()
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error deleting university:", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

# Function to get all universities to create dropdown options for the top left widget and bottom left widget 2
def get_all_universities():
    """
    Returns a list of all universities for dropdown options.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT DISTINCT name FROM university ORDER BY name")
        results = [row[0] for row in mysql_cursor.fetchall()]
        mysql_cursor.close()
        mysql_conn.close()
        return results
    except mysql.connector.Error as e:
        print("Error fetching universities:", e)
        return []


## Top Left Widget (citation rankings)
# Function for Searching by university and get citation ranking
def get_citation_ranking(name: str):
    """
    Searches by university and gets the top 10 citation rankings amongst faculty

    Parameters
    ----------
    name : str
        The name of the university.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        # Start transaction
        mysql_conn.start_transaction()

        # Query to get top 10 faculty by citation count for the given university
        mysql_cursor.execute("""SELECT f.name, SUM(p.num_citations) AS totalCitations
                             FROM faculty f 
                             JOIN university u ON u.id = f.university_id
                             JOIN faculty_publication fp ON fp.faculty_id = f.id
                             JOIN  publication p ON p.ID = fp.publication_id
                             WHERE u.name = %s 
                             GROUP BY f.name
                             ORDER BY totalCitations DESC
                             LIMIT 10""", (name, ))
        results = mysql_cursor.fetchall()
        columns = [desc[0] for desc in mysql_cursor.description]
        rows = [dict(zip(columns, row)) for row in results]
        return rows
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error fetching citation rankings: ", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def get_faculty_by_university(university_name: str):
    """
    Searches by university and gets a list of faculty

    Parameters
    ----------
    university_name : str
        The name of the university.
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        # Start transaction
        mysql_conn.start_transaction()

        # Query to get top 10 faculty by citation count for the given university
        mysql_cursor.execute("""SELECT f.name, f.id
                             FROM faculty f 
                             JOIN university u ON u.id = f.university_id
                             WHERE u.name = %s """, 
                             (university_name, ))
        results = mysql_cursor.fetchall()
        columns = [desc[0] for desc in mysql_cursor.description]
        rows = [dict(zip(columns, row)) for row in results]
        return rows
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error fetching faculty: ", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def get_publications_by_faculty(faculty_id: int):
    """
    Searches by faculty and gets the publications

    Parameters
    ----------
    faculty_id : int
        The id number for a faculty member
    """

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        # Start transaction
        mysql_conn.start_transaction()

        # Query to get top 10 faculty by citation count for the given university
        mysql_cursor.execute("""SELECT p.title, p.id
                             FROM faculty f 
                             JOIN faculty_publication fp ON fp.faculty_id = f.id
                             JOIN  publication p ON p.ID = fp.publication_id
                             WHERE f.id = %s 
                             """, (faculty_id, ))
        results = mysql_cursor.fetchall()
        columns = [desc[0] for desc in mysql_cursor.description]
        rows = [dict(zip(columns, row)) for row in results]
        return rows
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error fetching citation rankings: ", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def add_publication(faculty_id, data):
    """
    Adds a new publication and links it to a faculty member.

    Parameters
    ----------
    faculty_id : int
        The faculty member's ID.
    data : dict
        Dictionary with publication fields, e.g. {"title": "...", "venue": "...", "year": ..., "num_citations": ...}
    """
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_conn.start_transaction()

        # Get next available id for publication
        mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM publication")
        next_id = mysql_cursor.fetchone()[0]

        # Insert publication with all fields and explicit id
        mysql_cursor.execute(
            "INSERT INTO publication (id, title, venue, year) VALUES (%s, %s, %s, %s)",
            (
                next_id,
                data.get("title"),
                data.get("venue"),
                data.get("year")
            )
        )

        # Link to faculty
        mysql_cursor.execute(
            "INSERT INTO faculty_publication (faculty_id, publication_id) VALUES (%s, %s)",
            (faculty_id, next_id)
        )

        mysql_conn.commit()
        return next_id
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error adding publication:", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def update_publication(pub_id, updated_data):
    """
    Updates a publication's information.

    Parameters
    ----------
    pub_id : int
        The publication's ID.
    updated_data : dict
        Dictionary with fields to update, e.g. {"title": "...", "venue": "...", "year": ..., "num_citations": ...}
    """
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_conn.start_transaction()

        # Build dynamic SQL for only the fields provided
        fields = []
        values = []
        for field in ["title", "venue", "year", "num_citations"]:
            if field in updated_data and updated_data[field] is not None:
                fields.append(f"{field} = %s")
                values.append(updated_data[field])
        if not fields:
            # Nothing to update
            mysql_cursor.close()
            mysql_conn.close()
            return

        sql = f"UPDATE publication SET {', '.join(fields)} WHERE id = %s"
        values.append(pub_id)
        mysql_cursor.execute(sql, tuple(values))

        mysql_conn.commit()
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error updating publication:", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def delete_publication(pub_id):
    """
    Deletes a publication and its faculty link.

    Parameters
    ----------
    pub_id : int
        The publication's ID.
    """
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_conn.start_transaction()

        # Remove publication
        mysql_cursor.execute(
            "DELETE FROM faculty_publication WHERE publication_id = %s",
            (pub_id,)
        )

        mysql_conn.commit()
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        print("Error deleting publication:", e)
        raise
    finally:
        mysql_cursor.close()
        mysql_conn.close()

def get_publication(pub_id):
    """
    Searches by publication ID and gets the publication details

    Parameters
    ----------
    pub_id : int
        The ID of the publication.
    """

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT title, venue, year, num_citations FROM publication WHERE id = %s", (pub_id,)
        )
        result = cursor.fetchone()
        return result
    except Exception as e:
        print("Error fetching publication:", e)
        return None
    finally:
        cursor.close()
        conn.close()

