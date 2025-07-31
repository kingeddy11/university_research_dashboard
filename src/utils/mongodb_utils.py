import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


## MongoDB connection setup
port = os.getenv("MONGO_PORT")

mongo_client = MongoClient(f"mongodb://localhost:{port}/")
mongo_db = mongo_client["academicworld"]
print("Mongo connection successful")


## Top Right Widget (university publications over time)
# Create index on publications collection
top_right_index = mongo_db.publications.create_index([("id", 1)])
print("Index on publications.id created")

# Function to query university publications over time
def top_right_query(universities = None, years = None):
    """
    Aggregates publication counts by university and year.

    Parameters
    ----------
    universities : list, optional
        List of university names to filter by.
    years : list of length 2, optional
        List of publication years to filter by, i.e. [start_year, end_year].

    Returns
    -------
    list
        A list of aggregated publication counts by university and year.
    """

    # Error handling for invalid input types
    if universities and not all(isinstance(u, str) for u in universities):
        raise ValueError("All university names must be strings.")
    if years and not all(isinstance(y, int) for y in years):
        raise ValueError("All years must be integers.")
    
    # Building the aggregation pipeline
    pipeline = [
        { "$project": { "affiliation": 1, "publications": 1 } },
        {
            "$lookup": {
                "from": "publications",
                "localField": "publications",
                "foreignField": "id",
                "as": "pub_data"
            }
        },
        { "$unwind": "$pub_data" }
    ]

    match_conditions = {}
    if universities:
        match_conditions["affiliation.name"] = {"$in": universities}
    if years and len(years) == 2:
        match_conditions["pub_data.year"] = {"$gte": years[0], "$lte": years[1]}

    if match_conditions:
        pipeline.append({"$match": match_conditions})

    pipeline.extend([
        {
            "$group": {
                "_id": {
                    "university": "$affiliation.name",
                    "year": "$pub_data.year"
                },
                "university_publications": {"$sum": 1}
            }
        },
        {"$sort": {"_id.university": 1, "_id.year": 1}}
    ])

    results = mongo_db.faculty.aggregate(pipeline)

    return list(results)

# Function to get all universities to create dropdown options for the top right widget
def get_all_universities():
    """
    Returns a list of all universities for dropdown options.
    """

    universities = mongo_db.faculty.distinct("affiliation.name")
    return sorted(universities)

# Function to min and max years for the year range slider
def get_publication_year_range():
    """
    Returns the [min, max] range of publication years.
    """

    years = mongo_db.publications.distinct("year")
    valid_years = [year for year in years if isinstance(year, int) and year > 0]
    return [min(valid_years), max(valid_years)] if valid_years else [None, None]
