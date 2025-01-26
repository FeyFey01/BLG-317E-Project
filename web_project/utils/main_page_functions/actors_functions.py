from flask import Flask, jsonify, render_template, request
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")
# Load app configuration from config.py
app.config.from_object(Config)
# Initialize MySQL connection
mysql = MySQL(app)

def get_actors(sort_by=None, sort_order='ASC', filter_by=None, filter_value=None):
    try:
        cursor = mysql.connection.cursor()

        # Base query - Filtering only actors with "actor" in primaryProfession
        query = """
            SELECT 
                nb.nconst, nb.originalName, nb.birthYear, nb.deathYear, nb.knownName, nb.primaryProfession,
                tc.category, tc.characterName, tb.title, tb.startYear, tb.endYear,tb.tconst
            FROM 
                name_basics nb
            LEFT JOIN 
                title_cast tc ON nb.nconst = tc.nconst
            LEFT JOIN 
                title_basics tb ON tc.tconst = tb.tconst
            WHERE 
                nb.primaryProfession LIKE %s
        """
        values = ['%actor%']

        # Additional filtering
        if filter_value is not None:
            if filter_by in ['birthYear', 'deathYear']:
                query += f" AND {filter_by} = %s"
                values.append(filter_value)
            elif filter_by in ['originalName', 'knownName', 'primaryProfession']:
                query += f" AND {filter_by} LIKE %s"
                values.append(f"%{filter_value}%")

        # Sorting
        sort_by = sort_by if sort_by in ['originalName', 'birthYear', 'deathYear', 'knownName'] else 'originalName'
        sort_order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
        query += f" ORDER BY {sort_by} {sort_order}"

        # Execute query
        cursor.execute(query, tuple(values))
        data = cursor.fetchall()

        # Group movies by actor (nconst)
        actors = {}
        for row in data:
            nconst = row['nconst']
            if nconst not in actors:
                actors[nconst] = {
                    'originalName': row['originalName'],
                    'knownName': row['knownName'],
                    'birthYear': row['birthYear'],
                    'deathYear': row['deathYear'],
                    'primaryProfession': row['primaryProfession'],
                    'movies': [],
                    'nconst': row['nconst']
                }
            # Append movie details to the actor's 'movies' list
            movie_details = {
                'title': row['title'],
                'startYear': row['startYear'],
                'endYear': row['endYear'],
                'category': row['category'],
                'characterName': row['characterName'],
                'tconst': row['tconst']
            }
            actors[nconst]['movies'].append(movie_details)

        return list(actors.values())  # Return actors list

    except Exception as e:
        print(f"Error fetching actors: {e}")
        return None




# Add the delete function
def delete_actor(nconst):
    try:
        cursor = mysql.connection.cursor()
        # Delete the actor from the name_basics table
        query = "DELETE FROM name_basics WHERE nconst = %s"
        cursor.execute(query, (nconst,))
        mysql.connection.commit()  # Commit the changes
        cursor.close()
        print(f"Actor with nconst {nconst} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting actor with nconst {nconst}: {e}")
        return False

# Add the update function
def update_actor(nconst, known_name=None, birth_year=None, death_year=None, primary_profession=None):
    try:
        cursor = mysql.connection.cursor()
        
        # Prepare the update query with dynamic values
        query = "UPDATE name_basics SET "
        updates = []
        values = []

        if known_name:
            updates.append("knownName = %s")
            values.append(known_name)
        if birth_year:
            updates.append("birthYear = %s")
            values.append(birth_year)
        if death_year:
            updates.append("deathYear = %s")
            values.append(death_year)
        if primary_profession:
            updates.append("primaryProfession = %s")
            values.append(primary_profession)

        # Join all updates with commas and finish the query
        query += ", ".join(updates)
        query += " WHERE nconst = %s"
        values.append(nconst)

        cursor.execute(query, tuple(values))  # Execute the update
        mysql.connection.commit()  # Commit the changes
        cursor.close()
        print(f"Actor with nconst {nconst} updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating actor with nconst {nconst}: {e}")
        return False
    