from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)
# This function should already exist in your cast_function.py
def fetch_crew_and_cast_by_tconst(tconst):
    """Fetch the details of a movie's crew and cast based on tconst."""
    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT 
            tb.tconst,
            tb.title,
            tb.titleType,
            tb.isAdult,
            tb.startYear,
            tb.endYear,
            tb.genre,
            tc.directorNconst,
            director.originalName AS directorName,
            tc.writerNconst,
            writer.originalName AS writerName,
            tcst.nconst AS castNconst,
            cast.originalName AS castName,
            tcst.category AS castCategory,
            tcst.characterName AS castCharacter
        FROM 
            title_basics tb
        LEFT JOIN title_crew tc 
            ON tb.tconst = tc.tconst
        LEFT JOIN name_basics director 
            ON tc.directorNconst = director.nconst
        LEFT JOIN name_basics writer 
            ON tc.writerNconst = writer.nconst
        LEFT JOIN title_cast tcst 
            ON tb.tconst = tcst.tconst
        LEFT JOIN name_basics cast 
            ON tcst.nconst = cast.nconst
        WHERE 
            tb.tconst = %s
        ORDER BY 
            tb.title
        """
        
        cursor.execute(query, (tconst,))
        data = cursor.fetchall()
        cursor.close()

        if not data:
            return None

        # Organize the data into a dictionary
        movie_info = {
            "tconst": data[0]['tconst'],
            "title": data[0]['title'],
            "title_type": data[0]['titleType'],
            "is_adult": data[0]['isAdult'],
            "start_year": data[0]['startYear'],
            "end_year": data[0]['endYear'],
            "genre": data[0]['genre'],
            "director": data[0]['directorName'],
            "writer": data[0]['writerName'],
            "cast": []
        }

        # Extract the cast information
        for row in data:
            if row['castName']:
                movie_info['cast'].append({
                    'nconst': row['castNconst'],
                    'original_name': row['castName'],
                    'category': row['castCategory'],
                    'character_name': row['castCharacter'],
                })

        return movie_info

    except Exception as e:
        print(f"Error fetching crew and cast for tconst {tconst}: {e}")
        return None
    

    
def update_crew_and_cast_by_tconst(tconst, director_nconst=None, writer_nconst=None, cast_info=None):
    try:
        cursor = mysql.connection.cursor()

        # Update the director if a new one is provided
        if director_nconst:
            cursor.execute("""
                UPDATE title_crew 
                SET directorNconst = %s 
                WHERE tconst = %s
            """, (director_nconst, tconst))

        # Update the writer if a new one is provided
        if writer_nconst:
            cursor.execute("""
                UPDATE title_crew 
                SET writerNconst = %s 
                WHERE tconst = %s
            """, (writer_nconst, tconst))

        # Update the cast information if provided
        if cast_info:
            for cast in cast_info:
                cast_nconst = cast.get('nconst')
                category = cast.get('category')
                character_name = cast.get('character_name')

                if cast_nconst:  # Ensure the cast member exists
                    cursor.execute("""
                        UPDATE title_cast 
                        SET category = %s, characterName = %s 
                        WHERE tconst = %s AND nconst = %s
                    """, (category, character_name, tconst, cast_nconst))

        # Commit the changes to the database
        mysql.connection.commit()

        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating crew and cast for tconst {tconst}: {e}")
        mysql.connection.rollback()  # Rollback in case of error
        return False


