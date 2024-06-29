import os
import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Item, Recipes
from . import db

views = Blueprint("views", __name__)
totals = {}

def calculate_totals(user):
    """
    Calculates the total nutritional intake for the user.
    """
    totals = {category: 0 for category in ["cals", "fats", "protein", "carbs"]}
    for item in user.items:
        totals["cals"] += item.cals
        totals["protein"] += item.protein
        totals["fats"] += item.fats
        totals["carbs"] += item.carbs
    totals["percent_intake"] = (totals["cals"] / user.recommended_intake) * 100
    
    return totals

@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    global totals
    if request.method == "POST":
        item = request.form.get("item")
        cals = request.form.get("cals")        
        fats = request.form.get("fats")
        protein = request.form.get("protein")
        carbs = request.form.get("carbs")

        def validate(txt):
            """
            Validates that the given text is a number.
            """
            return txt.strip().isnumeric()
        
        if not item:
            flash("Invalid entrance for item", category="error")
        elif not cals or not protein or not fats or not carbs:
            flash("Calories, protein, fat, and carbs cannot be blank", category="error")
        elif not (validate(cals) and validate(fats) and validate(protein) and validate(carbs)):
            flash("Calories, protein, fat, and carbs must be a number", category="error")
        else:
            new_item = Item(
                carbs=carbs.strip(), cals=cals.strip(), fats=fats.strip(),
                protein=protein.strip(), name=item.strip(), user_id=current_user.id
            )
            db.session.add(new_item)
            db.session.commit()
            flash("Item added!", category="success")
    
    totals = calculate_totals(current_user)
    return render_template("home.html", user=current_user, user_dict=totals)

@views.route("/get-recipes")
def get_recipes():
    """
    Fetches and displays all recipes.
    """
    recipes_list = Recipes.query.order_by(Recipes.id).all()
    return render_template("get_recipes.html", recipes=recipes_list, user=current_user)

@views.route('/search_recipes', methods=['GET', 'POST'])
def search_recipes():
    """
    Searches for recipes by name.
    """
    query = request.args.get('query')
    filtered_recipes = Recipes.query.filter(Recipes.name.ilike(f'%{query}%')).all()
    return render_template('get_recipes.html', recipes=filtered_recipes, query=query, user=current_user)

@views.route("/getpythondata")
def get_python_data():
    """
    Transfers user data as a Python dictionary to the frontend for JavaScript to handle.
    """
    return json.dumps(totals)

@views.route("/delete-item", methods=["POST"])
def delete_item():
    """
    Deletes an item based on the ID received from the frontend.
    """
    item = json.loads(request.data)
    item_id = item["itemId"]
    item = Item.query.get(item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    
    return jsonify({})

@views.route("/profile", methods=["POST", "GET"])
def profile():
    """
    Renders the user profile page.
    """
    return render_template("profile.html", user=current_user)

@views.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """
    Updates the user's profile information.
    """
    if request.method == 'POST':
        current_user.age = request.form.get('age')
        current_user.gender = request.form.get('gender')
        current_user.weight = request.form.get('weight')
        current_user.height = request.form.get('height')
        current_user.dietary_preferences = request.form.get('dietary_preferences')
        current_user.allergies = request.form.get('allergies')
        current_user.health_goals = request.form.get('health_goals')
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('views.profile'))
    return render_template('update_profile.html', user=current_user)

@views.route('/update_profile_image', methods=['POST'])
@login_required
def update_profile_image():
    """
    Updates the user's profile image.
    """
    if 'profile_image' in request.files:
        image = request.files['profile_image']
        if image.filename != '':
            dir = os.path.join(os.path.dirname(__file__), 'static/profile_images')
            if not os.path.exists(dir):
                os.makedirs(dir)
            image_path = os.path.join(dir, f'{current_user.id}.jpg')
            image.save(image_path)

            current_user.profile_image = f'profile_images/{current_user.id}.jpg'
            db.session.commit()
            flash('Profile image updated successfully')
    return redirect(url_for('views.profile'))

@views.route("/diet_goal", methods=["POST", "GET"])
def diet_goal():
    global totals
    if request.method == "POST":
        item = request.form.get("item")
        cals = request.form.get("cals")        
        fats = request.form.get("fats")
        protein = request.form.get("protein")
        carbs = request.form.get("carbs")

        def validate(txt):
            """
            Validates that the given text is a number.
            """
            return txt.strip().isnumeric()
        
        if not item:
            flash("Invalid entrance for item", category="error")
        elif not cals or not protein or not fats or not carbs:
            flash("Calories, protein, fat, and carbs cannot be blank", category="error")
        elif not (validate(cals) and validate(fats) and validate(protein) and validate(carbs)):
            flash("Calories, protein, fat, and carbs must be a number", category="error")
        else:
            new_item = Item(
                carbs=carbs.strip(), cals=cals.strip(), fats=fats.strip(),
                protein=protein.strip(), name=item.strip(), user_id=current_user.id
            )
            db.session.add(new_item)
            db.session.commit()
            flash("Item added!", category="success")
    
    totals = calculate_totals(current_user)
    return render_template("diet_goal.html", user=current_user, user_dict=totals)

@views.route("/update-items", methods=["POST"])
def update_items():
    """
    Updates items based on the date received from the frontend.
    Deletes items if the database date is older than the JavaScript date.
    """
    def comp_js_db_date(js_date, db_datetime):
        """
        Compares the JavaScript date with the database date.
        Returns True if the item should be deleted.
        """
        month_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        js_m, js_d, js_y = map(int, js_date.split("/"))
        db_m, db_d, db_y = map(int, db_datetime.strftime('%m-%d-%Y').split("-"))
        h, m, s = map(int, db_datetime.strftime('%H:%M:%S').split(":"))

        db_date_in_hours = db_y * 8760 + sum(month_days[m] * 24 for m in range(1, db_m)) + db_d * 24 + h - 5
        js_date_in_hours = js_y * 8760 + sum(month_days[m] * 24 for m in range(1, js_m + 1)) + js_d * 24

        return js_date_in_hours >= db_date_in_hours

    date = json.loads(request.data)
    for item in current_user.items:
        if comp_js_db_date(date["date"], item.date):
            db.session.delete(item)
            db.session.commit()
    return jsonify({})
