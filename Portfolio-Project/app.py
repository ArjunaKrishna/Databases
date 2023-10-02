from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask import jsonify
from database.db_connector import connect_to_database, execute_query
import database.db_connector as db
import os
import secrets

app = Flask(__name__)
db_connection = connect_to_database()
app.secret_key = secrets.token_hex(16)

mysql = MySQL(app)

# ------------------------------MAIN———————————————# 
@app.route('/',methods=["GET"])
def home():
    if request.method == "GET": 
            return render_template("base.j2")

###########################################################
########          ANIMALS - CRUD - BEGIN           ########
###########################################################

#### ANIMALS CREATE ####
@app.route('/animals/create', methods=['GET', 'POST'])
def animalsCreate():
    if request.method == 'POST':
        name = request.form['name']
        breed = request.form['breed']
        age = request.form['age']
        health_status = request.form['health_status']
        query = "INSERT INTO Animals (name, breed, age, health_status) VALUES (%s, %s, %s, %s)"
        cursor = execute_query(query, (name, breed, age, health_status))
        return redirect('/animals')
    else:
        return render_template("animals_create.j2")

#### ANIMALS READ/RETRIEVE ####
@app.route('/animals', methods=["GET"])
def animals_retrieve():
    db_entity = "Animals"
    query = "SELECT * FROM Animals;"
    cursor = execute_query(query)
    results = cursor.fetchall()
    cursor.close()
    return render_template("animals.j2", page_title=db_entity, animals=results)

#### ANIMALS UPDATE ####
@app.route('/animals/update', methods=['GET', 'POST'])
def update_animal():
    if request.method == "GET":
        animal_id = request.args.get('id')
        query = "SELECT * FROM Animals WHERE animal_id = %s"
        cursor = execute_query(query, (animal_id,))
        animal_data = cursor.fetchone()
        if animal_data is None:
            return render_template("error.j2", message="Animal not found.")
        formPrefillData = dict()
        formPrefillData['name'] = animal_data['name']
        formPrefillData['breed'] = animal_data['breed']
        formPrefillData['age'] = animal_data['age']
        formPrefillData['health_status'] = animal_data['health_status']
        return render_template("animals_edit.j2", animal_data=formPrefillData)
    elif request.method == "POST":
        animal_id = request.form['animal_id']
        name = request.form['name']
        breed = request.form['breed']
        age = request.form['age']
        health_status = request.form['health_status']
        query = "UPDATE Animals SET name=%s, breed=%s, age=%s, health_status=%s WHERE animal_id=%s"
        cursor = execute_query(query, (name, breed, age, health_status, animal_id))
        if cursor is None:
            flash("Failed to update animal.")
        else:
            flash("Animal updated successfully.")
        return redirect(url_for('animals_retrieve'))

@app.route('/animals/delete', methods=['GET', 'POST'])
def delete_animal():
    if request.method == "GET":
        animal_id = request.args.get('id')
        query = "SELECT * FROM Animals WHERE animal_id = %s"
        cursor = execute_query(query, (animal_id,))
        animal_data = cursor.fetchone()
        if animal_data is None:
            return render_template("error.j2", message="Animal not found.")
        return render_template("delete_animals.j2", animal_data=animal_data)
    elif request.method == "POST":
        animal_id = request.form['animal_id']
        
        # Delete all related records from Adoptions table
        query = "DELETE FROM Adoptions WHERE animal_id = %s"
        cursor = execute_query(query, (animal_id,))
        
        # Delete all related records from Volunteer_Animals table
        query = "DELETE FROM Volunteer_Animals WHERE animal_id = %s"
        cursor = execute_query(query, (animal_id,))
        
        # Check for donations before deleting animal
        check_query = "SELECT * FROM Donations WHERE animal_id = %s"
        cursor = execute_query(check_query, (animal_id,))
        donation_data = cursor.fetchone()
        if donation_data is not None:
            flash("Cannot delete animal because it has associated donations.")
            return redirect(url_for('animals_retrieve'))
        
        # If no donations, delete animal record
        delete_query = "DELETE FROM Animals WHERE animal_id = %s"
        cursor = execute_query(delete_query, (animal_id,))
        flash("Animal deleted successfully.")
        return redirect(url_for('animals_retrieve'))


###########################################################
#########          ANIMALS - CRUD - END          ##########
###########################################################

###########################################################
#########        ADOPTIONS - CRUD - BEGIN	      #########      
###########################################################

#### ADOPTIONS READ/RETRIEVE ####
@app.route('/adoptions', methods=['GET'])
def adoptionIndex():
    # Create query strings and execute to retrieve required data from database
    db_entity = "Adoptions"
    query = "SELECT * FROM Adoptions;"
    cursor = execute_query(query)
    if cursor:
        results = cursor.fetchall()
        cursor.close()
        return render_template("adoptions.j2", title_page=db_entity, adoptions=results)
    else:
        error_message = "Error retrieving data from database"
        print(f"Error executing query {query}")
        return render_template('adoptions.j2', rows=[], alerts=[("danger", error_message)])




#### ADOPTIONS CREATE ####
@app.route("/adoptions/create", methods=["GET", "POST"])
def adoptionCreate():
    db_connection = db.connect_to_database()
    if request.method == "POST":
        adopter_name = request.form["adopterName"]
        adoption_date = request.form["adoptionDate"]
        animal_id = request.form["animalId"]
        volunteer_id = request.form["volunteerId"]
        query = "INSERT INTO Adoptions (adopter_name, adoption_date, animal_id, volunteer_id) VALUES (%s, %s, %s, %s)"
        data = (adopter_name, adoption_date, animal_id, volunteer_id)
        db.execute_query(query, data, db_connection)
        flash("Success! Database updated!")
        return redirect(url_for('adoptionIndex'))
    # Handle the GET request
    animals_query = "SELECT * FROM Animals"
    volunteers_query = "SELECT * FROM Volunteers"

    cursor = db.execute_query(animals_query, None, db_connection)
    animals = cursor.fetchall()
    cursor = db.execute_query(volunteers_query, None, db_connection)
    volunteers = cursor.fetchall()

    return render_template("adoptions_create.j2", animals=animals, volunteers=volunteers)



#### ADOPTIONS UPDATE ####
@app.route('/adoptions/update', methods=["GET", "POST"])
def update_adoption():
    db_connection = db.connect_to_database()
    form_prefill_data = {'adopterIds': [], 'animalIds': []}
    if request.method == "GET":
        adoption_id = request.args.get('id')
        if not adoption_id:
            return render_template("error.j2", message="Invalid request: no adoption ID provided.")
        query = f"SELECT * FROM Adoptions WHERE adoption_id = %s"
        cursor = db.execute_query(connection=db_connection, query=query, query_params=(adoption_id,))
        adoption = cursor.fetchone()
        if not adoption:
            return render_template("error.j2", message=f"Adoption record with ID {adoption_id} does not exist.")
        query = "SELECT adoption_id, adopter_name FROM Adoptions;"
        cursor = db.execute_query(connection=db_connection, query=query)
        if cursor:
            form_prefill_data['adopterIds'] = cursor.fetchall()
        query = "SELECT animal_id, name FROM Animals;"
        cursor = db.execute_query(connection=db_connection, query=query)
        if cursor:
            form_prefill_data['animalIds'] = cursor.fetchall()
        return render_template("adoptions_update.j2", updateRecord=adoption, formPrefillData=form_prefill_data)
    elif request.method == "POST":
        adoption_id = request.form.get('adoptionId')
        animal_id = request.form.get('animalId')
        adopter_name = request.form.get('adopterName')
        adoption_date = request.form.get('adoptionDate')
        volunteer_id = request.form.get('volunteerId')
        query = "UPDATE Adoptions SET adopter_name = %s, adoption_date = %s, animal_id = %s, volunteer_id = %s WHERE adoption_id = %s"
        query_params = (adopter_name, adoption_date, animal_id, volunteer_id, adoption_id)
        cursor = db.execute_query(connection=db_connection, query=query, query_params=query_params)
        return redirect(url_for('adoptionIndex'))


#### ADOPTIONS DELETE ####
@app.route('/adoptions/delete', methods=['GET', 'POST'])
def delete_adoption():
    delete_query = "DELETE FROM Adoptions WHERE adoption_id = %s"
    if request.method == "GET":
        adoption_id = request.args.get('adoption_id')
        query = "SELECT * FROM Adoptions WHERE adoption_id = %s"
        db_connection = db.connect_to_database()
        cursor = db.execute_query(query=query, query_params=(adoption_id,), connection=db_connection)
        adoption_data = cursor.fetchone()
        return render_template("delete_adoption.j2", adoption_data=adoption_data)
    elif request.method == "POST":
        adoption_id = request.form['adoption_id']
        db_connection = db.connect_to_database()
        cursor = db_connection.cursor()
        cursor.execute(delete_query, (adoption_id,))
        db_connection.commit()
        flash("Adoption deleted!")
        return redirect(url_for('adoptionIndex'))


#### ADOPTION HISTORY ####
@app.route('/adoption-history')
def adoption_history():
    query = "SELECT pet_name, species, breed, age, sex, description, adopter_name, adoption_date \
             FROM Adoption JOIN Animals ON Adoption.animal_id=Animals.animal_id \
             ORDER BY adoption_date DESC"
    adoptions = execute_query(query)
    return render_template('adoption_history.j2', adoptions=adoptions)

###########################################################
#########        ADOPTIONS - CRUD - END	          #########
###########################################################

###########################################################
#########        DONATIONS - CRUD - BEGIN          ########
###########################################################

def fetch_animal_ids():
    query = "SELECT animal_id, name FROM Animals;"
    cursor = execute_query(query, None, connection=db_connection)
    if cursor:
        return cursor.fetchall()
    else:
        return None

#### DONATIONS CREATE ####
@app.route("/donations/create", methods=["GET", "POST"])
def donationsCreate():
    alerts = None
    if request.method == "POST":
        donor_name = request.form["donor_name"]
        amount = request.form["amount"]
        date_of_donation = request.form["date_of_donation"]
        animal_id = request.form["animal_id"]
        query = "INSERT INTO Donations (donor_name, amount, date_of_donation, animal_id) VALUES (%s, %s, %s, %s)"
        data = (donor_name, amount, date_of_donation, animal_id)
        execute_query(query, data=data)
        alerts = ("Donation added successfully!", False)
    query = '''
        SELECT Donations.donation_id, Donations.donor_name, Donations.amount, Donations.date_of_donation, Animals.name as animal_name
        FROM Donations
        JOIN Animals ON Donations.animal_id = Animals.animal_id;
    '''
    with connect_to_database() as db_connection:
        cursor = execute_query(query, connection=db_connection)
        donations = cursor.fetchall()
    return render_template("donations.j2", donations=donations, alerts=alerts)


#### DONATIONS READ/RETRIEVE ####
@app.route("/donations", methods=["GET", "POST"])
def donations():
    if request.method == "POST":
        donor_name = request.form["donorName"]
        amount = request.form["amount"]
        date_of_donation = request.form["date_of_donation"]
        animal_id = request.form["animal_id"]
        query = "INSERT INTO Donations (donor_name, amount, date_of_donation, animal_id) VALUES (%s, %s, %s, %s)"
        data = (donor_name, amount, date_of_donation, animal_id)
        execute_query(query, query_params=data)
        alerts = ("Donation added successfully!", False)
    query = '''
        SELECT Donations.donation_id, Donations.donor_name, Donations.amount, Donations.date_of_donation, Animals.name as animal_name
        FROM Donations
        JOIN Animals ON Donations.animal_id = Animals.animal_id;
    '''
    cursor = db_connection.cursor()
    donations = execute_query(query)
    cursor.close()
    
    # Add this query to fetch the list of animals
    animal_query = "SELECT animal_id, name FROM Animals;"
    cursor = db_connection.cursor()
    animals = execute_query(animal_query)
    cursor.close()
    return render_template("donations.j2", donations=donations, animals=animals)
    
    # Add this query to fetch the list of animals
    animal_query = "SELECT animal_id, name FROM Animals;"
    cursor = db_connection.cursor()
    animals = execute_query(animal_query)
    cursor.close()
    return render_template("donations.j2", donations=donations, animals=animals)

#### DONATIONS UPDATE ####
@app.route('/donations/update', methods=["GET", "POST"])
def update_donation():
    db_connection = connect_to_database()
    formPrefillData = {'animalIds': fetch_animal_ids()}
    if request.method == "GET":
        donation_id = request.args.get('donation_id')
        query = "SELECT * FROM Donations WHERE donation_id = %s"
        cursor = execute_query(query, query_params=[donation_id], connection=db_connection)
        updateRecord = cursor.fetchone()
        # Check if the entity exists
        if updateRecord is None:
            return render_template("error.j2", message=f"Record not found for donation_id: {donation_id}")

        query = "SELECT donor_id FROM Donors;"
        cursor = execute_query(query, connection=db_connection)
        if cursor:
            formPrefillData['donorIds'] = cursor.fetchall()
        return render_template('donations_update.j2', updateRecord=updateRecord, formPrefillData=formPrefillData)
    elif request.method == "POST":
        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
        query_params = [value for key, value in form_data.items()]
        query_params.append(request.args.get("donation_id"))
        query = "UPDATE Donations SET " + ', '.join([f"{key} = %s" for key in request.form.keys()]) + " WHERE donation_id = %s"
        cursor = execute_query(query, query_params=tuple(query_params), connection=db_connection)
        return redirect(url_for('donations'))

#### DONATIONS DELETE ####
@app.route('/donations/delete', methods=['GET', 'POST'])
def delete_donation():
    db_connection = connect_to_database()
    if request.method == 'GET':
        donation_id = request.args.get('donation_id')
        query = "SELECT Donations.*, Animals.name AS animal_name FROM Donations JOIN Animals ON Donations.animal_id = Animals.animal_id WHERE donation_id = %s"
        cursor = execute_query(query, query_params=[donation_id], connection=db_connection)
        donation = cursor.fetchone()
        if donation is None:
            return render_template("error.j2", message=f"Record not found for donation_id: {donation_id}")
        return render_template("delete_donations.j2", donation=donation)
    elif request.method == 'POST':
        donation_id = request.form['donation_id']
        delete_query = "DELETE FROM Donations WHERE donation_id = %s"
        cursor = execute_query(delete_query, query_params=[donation_id], connection=db_connection)
        return redirect(url_for('donations'))



###########################################################
#########        DONATIONS - CRUD - END	          #########        
###########################################################

###########################################################
##########       VOLUNTEERS - CRUD - BEGIN	      #########        
###########################################################

#### VOLUNTEERS CREATE ####
@app.route('/volunteers/create', methods=["GET", "POST"])
def volunteersCreate():
    dbEntity = "Volunteers"
    if request.method == "POST":
        volName = request.form["name"]
        volContactInfo = request.form["contact_info"]
        volHours = request.form["hours_volunteered"]
        query = "INSERT INTO Volunteers (volunteer_id, name, contact_info, hours_volunteered) VALUES (NULL, %s, %s, %s);"
        db_connection = db.connect_to_database()
        cursor = db.execute_query(query, (volName, volContactInfo, volHours), db_connection)
        flash('Volunteer created successfully!', 'success')
        return redirect(url_for('volunteersList'))
    else:
        return render_template("volunteers_create.j2")

#### VOLUNTEERS READ/RETRIEVE ####
@app.route('/volunteers', methods=["GET"])
def volunteersList():
    db_entity = "Volunteers"
    query = "SELECT * FROM Volunteers;"
    db_connection = connect_to_database()
    cursor = execute_query(query, connection=db_connection)
    results = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return render_template("volunteersList.j2", title_page_two=db_entity, volunteers=results)


#### VOLUNTEERS UPDATE ####
@app.route('/volunteers/update', methods=["GET", "POST"])
def update_volunteer():
    if request.method == "GET":
        volunteer_id = request.args.get('volunteer_id')
        query = "SELECT * FROM Volunteers WHERE volunteer_id = %s"
        db_connection = db.connect_to_database()
        cursor = db.execute_query(query=query, query_params=(volunteer_id,), connection=db_connection)
        updateRecord = cursor.fetchone()
        # Check if the entity exists
        if updateRecord is None:
            return render_template("error.j2", message="Record not found.")
        return render_template('volunteers_update.j2', updateRecord=updateRecord)
    elif request.method == "POST":
        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
        query_params = [value for key, value in form_data.items()]
        query_params.append(request.args.get("volunteer_id"))
        query = f"UPDATE Volunteers SET " + ', '.join([f"{key} = %s" for key in request.form.keys()]) + f" WHERE volunteer_id = %s"
        db_connection = db.connect_to_database()
        db.execute_query(query=query, query_params=query_params, connection=db_connection)
        return redirect(url_for('volunteersList'))


#### VOLUNTEERS DELETE ####
@app.route('/volunteers/delete', methods=['GET', 'POST'])
def delete_volunteer():
    delete_query = "DELETE FROM Volunteers WHERE volunteer_id = %s"
    if request.method == "GET":
        volunteer_id = request.args.get('volunteer_id')
        query = "SELECT * FROM Volunteers WHERE volunteer_id = %s" 
        db_connection = db.connect_to_database()
        cursor = db.execute_query(query=query, query_params=(volunteer_id,), connection=db_connection)
        if cursor is None:
            return render_template("error.j2", message="Error occurred during deletion.")
        volunteer_data = cursor.fetchone()
        return render_template("delete_volunteer.j2", volunteer_data=volunteer_data)
    
    elif request.method == "POST":
        volunteer_id = request.form['volunteer_id']
        db_connection = db.connect_to_database()
        cursor = db.execute_query(query=delete_query, query_params=(volunteer_id,), connection=db_connection)
        if cursor is None:
            return render_template("error.j2", message="Error occurred during deletion.")
        flash("Volunteer deleted successfully.")
        return redirect(url_for('volunteersList'))


###########################################################
#########        VOLUNTEERS - CRUD - END        ###########
###########################################################

###########################################################
#######  VOLUNTEER_ANIMALS -  CRUD  -   BEGIN     #########
###########################################################

@app.route('/volunteer_animals', methods=["GET", "POST"])
def volunteer_animals_retrieve():
    db_connection = connect_to_database()
    if request.method == "GET" and 'retrieveAll' not in request.args:
        # For retrieving volunteer-animals assignments with volunteers and animals names
        query = "SELECT Volunteer_Animals.volunteer_id, Volunteers.name AS volunteer_name, Volunteer_Animals.animal_id, Animals.name AS animal_name, Volunteer_Animals.hours_volunteered " \
                "FROM Volunteer_Animals " \
                "JOIN Volunteers ON Volunteer_Animals.volunteer_id = Volunteers.volunteer_id " \
                "JOIN Animals ON Volunteer_Animals.animal_id = Animals.animal_id"

        cursor = execute_query(query, connection=db_connection)
        if cursor is not None:
            results = cursor.fetchall()
            return render_template('volunteer_animals.j2', volunteer_animals=results)
    elif request.method == "GET" and 'retrieveAll' in request.args:
        query = "SELECT Volunteer_Animals.volunteer_id, Volunteers.name, Volunteer_Animals.animal_id, Animals.name, Volunteer_Animals.hours_volunteered " \
                "FROM Volunteer_Animals " \
                "JOIN Volunteers ON Volunteer_Animals.volunteer_id = Volunteers.volunteer_id " \
                "JOIN Animals ON Volunteer_Animals.animal_id = Animals.animal_id"
        cursor = execute_query(query, connection=db_connection)
        if cursor is not None:
            results = cursor.fetchall()
            return jsonify(results)
    return redirect('/volunteer_animals')


#### VOLUNTEER ANIMALS CREATE ####
@app.route('/volunteer_animals/create', methods=['GET', 'POST'])
def volunteer_animal_create():
    with connect_to_database() as db_connection:
        # Get data needed to populate form select inputs
        get_animals_query = "SELECT animal_id, name FROM Animals"
        get_volunteers_query = "SELECT volunteer_id, name FROM Volunteers"
        animals = execute_query(get_animals_query, connection=db_connection).fetchall()
        volunteers = execute_query(get_volunteers_query, connection=db_connection).fetchall()

        if request.method == 'POST':
            volunteer_id = request.form['volunteers']
            animal_id = request.form['animals']
            hours_volunteered = request.form['hours_volunteered']
            insert_va_query = "INSERT INTO Volunteer_Animals (volunteer_id, animal_id, hours_volunteered) VALUES (%s, %s, %s)"
            execute_query(insert_va_query, query_params=(volunteer_id, animal_id, hours_volunteered), connection=db_connection)
            flash('Volunteer-animal assignment created successfully!', 'success')
            return redirect('/volunteer_animals')
            
        return render_template('volunteer_animals_create.j2', animals=animals, volunteers=volunteers)

#### VOLUNTEER ANIMALS DELETE ####
@app.route('/volunteer_animals/delete/<int:volunteer_id>/<int:animal_id>', methods=['POST'])
def volunteer_animals_delete(volunteer_id, animal_id):
    with connect_to_database() as db_connection:
        # Check for any donations associated with the animal before deletion
        check_query = "SELECT * FROM Donations WHERE animal_id = %s"
        cursor = execute_query(check_query, query_params=(animal_id,), connection=db_connection)
        donation_data = cursor.fetchone()
        if donation_data is not None:
            # Delete the donation records associated with the animal
            delete_donation_query = "DELETE FROM Donations WHERE animal_id = %s"
            execute_query(delete_donation_query, query_params=(animal_id,), connection=db_connection)
        # Delete the volunteer-animal assignment
        delete_va_query = "DELETE FROM Volunteer_Animals WHERE volunteer_id = %s AND animal_id = %s"
        execute_query(delete_va_query, query_params=(volunteer_id, animal_id), connection=db_connection)

    flash("Volunteer-Animal assignment deleted successfully", "success")
    return redirect(url_for('volunteer_animals_retrieve'))


@app.route('/volunteer_animals_update/<int:volunteer_id>/<int:animal_id>', methods=['GET', 'POST'])
def volunteer_animals_update(volunteer_id, animal_id):
    db_connection = connect_to_database()
    
    # Get the volunteer from the database
    query_volunteer = "SELECT * FROM Volunteers WHERE volunteer_id = %s"
    cursor_volunteer = execute_query(query_volunteer, query_params=(volunteer_id,), connection=db_connection)
    volunteer = cursor_volunteer.fetchone()
    # Get the animal from the database
    query_animal = "SELECT * FROM Animals WHERE animal_id = %s"
    cursor_animal = execute_query(query_animal, query_params=(animal_id,), connection=db_connection)
    animal = cursor_animal.fetchone()
    # Return error page if animal record is not found in the database
    if animal is None:
        return render_template('error.j2', message='Animal not found')

    # Get the volunteer-animal assignment from the database
    query_va = "SELECT * FROM Volunteer_Animals WHERE volunteer_id = %s AND animal_id = %s"
    cursor_va = execute_query(query_va, query_params=(volunteer_id, animal_id), connection=db_connection)
    volunteer_animal = cursor_va.fetchone()

    if request.method == 'POST':
        hours_volunteered = request.form['hours_volunteered']
        update_va_query = "UPDATE Volunteer_Animals SET hours_volunteered = %s WHERE volunteer_id = %s AND animal_id = %s"
        cursor_va.execute(update_va_query, (hours_volunteered, volunteer_id, animal_id))
    db_connection.commit()
    db_connection.close()

    return render_template('volunteer_animals_update.j2', volunteer=volunteer, animal=animal, volunteer_animal=volunteer_animal)

###########################################################
#######  VOLUNTEER_ANIMALS -  CRUD  -   END       #########
###########################################################



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9771))
    app.run(port=port, debug=True)

# ------------------------------ERROR HANDLER------------------------------

@app.errorhandler(404)
def not_found(e):
    error_type = "404 Not Found"
    error_message = str(e)
    return render_template("error.j2", error_type=error_type, error_message=error_message), 404