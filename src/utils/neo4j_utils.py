from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

port = os.getenv("NEO4J_DB_PORT")
user = os.getenv("NEO4J_DB_USER")
password = os.getenv("NEO4J_DB_PASSWORD")
db_name = os.getenv("DB_NAME")

print(f"bolt://localhost:{port}/{db_name}")

neo4j_driver = GraphDatabase.driver(f"bolt://localhost:{port}/{db_name}", auth=(user, password))


# Function to comput KRC for top 10 universities with a given keyword
def get_krc(keyword):
    records, summary, keys = neo4j_driver.execute_query("""
        MATCH (faculty:FACULTY)-[:PUBLISH]->(p:PUBLICATION)-[l:LABEL_BY]->(k:KEYWORD {name: $keyword})
        MATCH (faculty)-[:AFFILIATION_WITH]->(univ:INSTITUTE)                                                
        WITH faculty, univ, SUM(toFloat(l.score) * toInteger(p.numCitations)) AS accumulated_citation
        WITH univ.name AS university, SUM(accumulated_citation) AS totalKRC
        RETURN university, totalKRC
        ORDER BY totalKRC DESC
        LIMIT 10

        """,
        {"keyword": keyword},
        database_=db_name,
    )
    return [record.data() for record in records]

