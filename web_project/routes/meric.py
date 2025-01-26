from flask import Flask, redirect, jsonify, url_for, request, render_template, Blueprint
from config import *
from utils.main_page_functions.actors_functions import *
from utils.detail_page_functions.crew_and_cast_functions import *  


# Create the Blueprint
actors_bp = Blueprint('actors', __name__)

# Route to list actors with sorting and filtering options
@actors_bp.route('/actors', methods=['GET'])
def actors_list():
    try:
        # Get query parameters for sorting and filtering
        sort_by = request.args.get('sort_by', None)
        sort_order = request.args.get('sort_order', 'ASC')
        filter_by = request.args.get('filter_by', None)
        filter_value = request.args.get('filter_value', None)
        
        # Call the function to get the actors from the database
        actors = get_actors(sort_by=sort_by, sort_order=sort_order, filter_by=filter_by, filter_value=filter_value)
        
        if actors:
            return render_template('main_pages/CRUD_pages_main/actors_crud/actors_list.html', actors=actors)
        else:
            return render_template('error.html', message="No actors found."), 404
    except Exception as e:
        print(f"Error fetching actors: {e}")
        return render_template('error.html', message="Failed to fetch actors."), 500



# Route to delete an actor
@actors_bp.route('/actors/delete/<string:nconst>', methods=['GET'])
def delete_actor_route(nconst):
    success = delete_actor(nconst)  # Call the delete function based on nconst
    if success:
        return redirect(url_for('actors.actors_list'))  # Redirect to the actors list
    else:
        return render_template('error.html', message="Failed to delete actor."), 500



@actors_bp.route('/actors/update/<string:nconst>', methods=['GET', 'POST'])
def update_actor_route(nconst):
    try:
        print(f"nconst: {nconst}")  # This will show up in the server logs.
        if request.method == 'POST':
            # Handle the form submission and update
            known_name = request.form.get('knownName')
            birth_year = request.form.get('birthYear')
            death_year = request.form.get('deathYear')
            primary_profession = request.form.get('primaryProfession')

            # Call the update function
            success = update_actor(nconst, known_name, birth_year, death_year, primary_profession)

            if success:
                return redirect(url_for('actors.actors_list'))  # Redirect to the actors list
            else:
                return render_template('error.html', message="Failed to update actor."), 500

        # GET request: Fetch the actor's current data and show in the form
        cursor = mysql.connection.cursor()
        query = """
            SELECT nconst, originalName, birthYear, deathYear, knownName, primaryProfession
            FROM name_basics
            WHERE nconst = %s
        """
        cursor.execute(query, (nconst,))
        actor = cursor.fetchone()
        cursor.close()

        if actor:
            return render_template('main_pages/CRUD_pages_main/actors_crud/update_actor.html', actor=actor)
        else:
            return render_template('error.html', message="Actor not found."), 404
    except Exception as e:
        print(f"Error updating actor with nconst {nconst}: {e}")
        return render_template('error.html', message="Failed to update actor."), 500






@actors_bp.route('/cast/<string:tconst>', methods=['GET'])
def cast_route(tconst):
    """Route to display crew and cast for a specific tconst."""
    try:
        # Fetch crew and cast details using the utility function
        result = fetch_crew_and_cast_by_tconst(tconst)

        if result:
            # Render the details page with the fetched result
            return render_template('detail_pages/crew_and_cast.html', result=result)
        else:
            # If no result is found, render an error page
            return render_template('error.html', message="No details found for the specified movie."), 404
    except Exception as e:
        print(f"Error fetching crew and cast for tconst {tconst}: {e}")
        # Render an error page if an exception occurs
        return render_template('error.html', message="Failed to fetch crew and cast details."), 500
    


@actors_bp.route('/cast/update/<string:tconst>', methods=['GET', 'POST'])
def cast_update_route(tconst):
    if request.method == 'GET':
        try:
            # Fetch movie details, including crew and cast
            result = fetch_crew_and_cast_by_tconst(tconst)

            if result:
                return render_template('detail_pages/update_crew_and_cast.html', movie=result)
            else:
                return render_template('error.html', message="No details found for the specified movie."), 404
        except Exception as e:
            print(f"Error fetching crew and cast for tconst {tconst}: {e}")
            return render_template('error.html', message="Failed to fetch crew and cast details."), 500

    elif request.method == 'POST':
        try:
            # Parse form data for cast updates
            cast_data = request.form.to_dict(flat=False)
            cast_members = []
            for index in range(len(cast_data['cast_data[][original_name]'])):
                cast_members.append({
                    'nconst': cast_data['cast_data[][nconst]'][index],
                    'category': cast_data['cast_data[][category]'][index],
                    'character_name': cast_data['cast_data[][character_name]'][index],
                })

            # Database operations
            cursor = mysql.connection.cursor()

            # Remove all existing cast for this tconst
            delete_query = "DELETE FROM title_cast WHERE tconst = %s"
            cursor.execute(delete_query, (tconst,))

            # Insert updated cast data
            insert_query = """
            INSERT INTO title_cast (tconst, nconst, category, characterName)
            VALUES (%s, %s, %s, %s)
            """
            for cast_member in cast_members:
                cursor.execute(insert_query, (
                    tconst,
                    cast_member['nconst'],
                    cast_member['category'],
                    cast_member['character_name']
                ))

            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('actors_bp.cast_route', tconst=tconst))

        except Exception as e:
            print(f"Error updating cast for tconst {tconst}: {e}")
            return render_template('error.html', message="Failed to update cast details."), 500
