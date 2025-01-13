# app.py
from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import logging
import re
from datetime import datetime,timezone,timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask_login import UserMixin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///infy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True)
    role = db.Column(db.String(50), nullable=False)
    verified = db.Column(db.Boolean, default=False)  # Added verified field
    last_login = db.Column(db.DateTime)

    def _repr_(self):
        return f'<User {self.name}>'

    def get_id(self):
        return str(self.id)  # Flask-Login expects a string for the user ID
    
    def is_active(self):
        return True  # Assume the user is always active (you can add more logic if needed)

    def is_authenticated(self):
        return True  # Return True if the user is authenticated
   
    def is_anonymous(self):
        return False  # Return False for regular users (anonymous should be for unauthenticated users)
# Add the new UserDetails model after existing models
class UserDetails(db.Model):
    __tablename__ = 'user_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('dog_details.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.Date, nullable=False)
    created_time = db.Column(db.Time, nullable=False)
    # Relationship with User model
    user = db.relationship('DogDetails', backref=db.backref('details', uselist=False))

class DogDetails(db.Model):
    __tablename__ = 'dog_details'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    event = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Dog {self.name}>'

class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Competition {self.title}>'
class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # Relationship with User and Competition models
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Check if there are any existing competitions in the database
        if not Competition.query.first():
            # Define the services list if the database is empty
            services = [
                Competition(
                    title="Agility Challenge",
                    date="24-03-2025",
                    time="10:00 am",
                    description="Test your dog's ability to complete an obstacle course following the commands.",
                    price=500
                ),
                Competition(
                    title="Obedience Trial",
                    date="25-03-2025",
                    time="12:00 am",
                    description="Dog and handler perform a series of obedience exercises to demonstrate their training.",
                    price=600
                ),
                Competition(
                    title="Best Costume Show",
                    date="26-03-2025",
                    time="12:00 am",
                    description="Elegant Tails, Happy Hearts",
                    price=700
                ),
            ]
            
            # Add the services to the database and commit
            db.session.add_all(services)
            db.session.commit()
            logger.info("Initial services added successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

@app.route('/')
def home():
    services = Competition.query.all()
    return render_template('index.html', services=services)

@app.route('/admin')
def admin():
    services = Competition.query.all()
    return render_template('admin.html', services=services)
def validate_service_data(title, date, time, description):
    errors = []
    
    if not title or len(title.strip()) < 3:
        errors.append("Title must be at least 3 characters long")
        
    try:
        datetime.strptime(date, '%d-%m-%Y')
    except ValueError:
        errors.append("Date must be in DD-MM-YYYY format")
        
    try:
        datetime.strptime(time.lower(), '%I:%M %p')
    except ValueError:
        errors.append("Time must be in HH:MM am/pm format (e.g., 10:00 am)")
        
    if not description or len(description.strip()) < 10:
        errors.append("Description must be at least 10 characters long")
        
    return errors

@app.route('/admin/events')
def admin_events():
    try:
        # Query all registrations
        registrations = db.session.query(DogDetails).all()
        
        # Group registrations by event
        events_dict = {}
        for registration in registrations:
            if registration.event not in events_dict:
                events_dict[registration.event] = []
            events_dict[registration.event].append({
                'id': registration.id,
                'name': registration.name,
                'breed': registration.breed,
                'age': registration.age,
            })
        
        return render_template('admin_events.html', events_dict=events_dict)
    except Exception as e:
        logger.error(f"Error fetching registrations: {e}")
        flash("Error loading registrations", "danger")
        return redirect(url_for('admin'))
    

@app.route('/admin/add_competition', methods=['GET', 'POST'])
def add_competition():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('competition_name')
            date = request.form.get('date')
            time = request.form.get('time')
            description = request.form.get('description')
            price = request.form.get('price')

            # Validate required fields
            if not all([title, date, time, description, price]):
                flash("All fields are required!", "danger")
                return render_template('add_competition.html')

            # Validate price to ensure it's a positive number
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value")
            except ValueError as e:
                flash(f"Invalid price: {e}", "danger")
                return render_template('add_competition.html')

            # Format date to match the existing format (assuming input is YYYY-MM-DD)
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d-%m-%Y')
            except ValueError as e:
                flash("Invalid date format!", "danger")
                return render_template('add_competition.html')

            # Format time to match the existing format (assuming input is HH:MM)
            try:
                time_obj = datetime.strptime(time, '%H:%M')
                formatted_time = time_obj.strftime('%I:%M %p').lower()
            except ValueError as e:
                flash("Invalid time format!", "danger")
                return render_template('add_competition.html')

            # Create new competition
            new_competition = Competition(
                title=title,
                date=formatted_date,
                time=formatted_time,
                description=description,
                price=price  # Add price to the competition
            )

            # Add to database with error handling
            try:
                db.session.add(new_competition)
                db.session.commit()
                flash("Competition added successfully!", "success")
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while adding competition: {e}")
                flash(f"Database error: {str(e)}", "danger")
                return render_template('add_competition.html')

        except Exception as e:
            logger.error(f"Error during competition addition: {e}")
            flash(f"Error: {str(e)}", "danger")
            return render_template('add_competition.html')

    # GET request
    return render_template('add_competition.html')


@app.route('/admin/delete_competition/<int:service_id>', methods=['POST'])
def delete_competition(service_id):
    try:
        service = Competition.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting service: {str(e)}")
        flash('Failed to delete event', 'danger')
    
    return redirect(url_for('admin'))


@app.route('/admin/edit_competition/<int:service_id>', methods=['GET', 'POST'])
def edit_competition(service_id):
    try:
        service = Competition.query.get_or_404(service_id)
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('competition_name')
            date = request.form.get('date')
            time = request.form.get('time')
            description = request.form.get('description')
            capacity = request.form.get('capacity')
            price = request.form.get('price')  # Get the price from the form

            # Validate form data
            errors = validate_service_data(title, date, time, description)
            
            if price:
                try:
                    price = float(price)
                    if price <= 0:
                        errors.append("Price must be a positive value")
                except ValueError:
                    errors.append("Price must be a valid number")
            
            if capacity:
                try:
                    capacity = int(capacity)
                    if capacity < service.registered_count:
                        errors.append("New capacity cannot be less than current registrations")
                    elif capacity <= 0:
                        errors.append("Capacity must be greater than 0")
                except ValueError:
                    errors.append("Capacity must be a valid number")

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('edit.html', service=service)

            # Update service details
            service.title = title
            service.date = date
            service.time = time
            service.description = description
            if capacity:
                service.capacity = capacity
            if price:
                service.price = price  # Update price in the service

            try:
                db.session.commit()
                flash("Competition updated successfully!", "success")
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while updating competition: {e}")
                flash("Error updating competition", "danger")
                return render_template('edit.html', service=service)

    except Exception as e:
        logger.error(f"Error in edit_competition route: {e}")
        flash("An error occurred while processing your request", "danger")
        return redirect(url_for('admin'))

    # GET request
    return render_template('edit.html', service=service)
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        service_id = data.get('service_id')
        user_id = 1  # In production, this should be the logged-in user's ID
        
        # Check if service exists
        service = Competition.query.get_or_404(service_id)
        
        # Check if item already in cart
        existing_cart_item = Cart.query.filter_by(
            service_id=service_id,
            user_id=user_id
        ).first()
        
        if existing_cart_item:
            return jsonify({
                'message': 'Item already in cart',
                'total_price': sum(item.price for item in Cart.query.filter_by(user_id=user_id).all())
            }), 200
            
        # Add new item to cart
        new_cart_item = Cart(
            service_id=service_id,
            user_id=user_id,
            title=service.title,
            date=service.date,
            time=service.time,
            price=service.price
        )
        
        db.session.add(new_cart_item)
        db.session.commit()
        
        # Calculate new total
        total_price = sum(item.price for item in Cart.query.filter_by(user_id=user_id).all())
        
        return jsonify({
            'message': 'Item added to cart successfully',
            'total_price': total_price
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({'message': 'Error adding item to cart'}), 500

@app.route('/cart')
def cart():
    try:
        user_id = 1  # In production, this should be the logged-in user's ID
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_price = sum(item.price for item in cart_items)
        return render_template('cart.html', cart_items=cart_items, total_price=total_price)
    except Exception as e:
        logger.error(f"Error accessing cart: {str(e)}")
        flash("Error accessing cart", "danger")
        return redirect(url_for('home'))


@app.route('/remove_from_cart/<int:service_id>', methods=['POST'])
def remove_from_cart(service_id):
    try:
        cart_item = Cart.query.get_or_404(service_id)
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing from cart: {str(e)}")
        return jsonify({'message': 'Error removing item from cart'}), 500


@app.route('/myevents')
def myevents():
    try:
        latest_registration = db.session.query(DogDetails).order_by(DogDetails.id.desc()).first()

        events_dict = {}
        if latest_registration:
            events_dict[latest_registration.event] = [{
                'id': latest_registration.id,
                'name': latest_registration.name,
                'breed': latest_registration.breed,
                'age': latest_registration.age,
            }]
        
        return render_template('myevents.html', events_dict=events_dict)
    except Exception as e:
        logger.error(f"Error fetching registration: {e}")
        flash("Error loading registration", "danger")
        return redirect(url_for('home'))

@app.route('/payments')
def payments():
    return render_template('payments.html')
@app.route('/details')
def details():
    return render_template('details.html')
@app.route('/validate_details', methods=['POST'])
def validate_details():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    # Validation logic
    if not name or not email or not phone or not address:
        flash("All fields are required!")
        return redirect('/details')

    if not re.match(r"^[6-9]\d{9}$", phone):
        flash("Phone number must be 10 digits and start with 6-9!")
        return redirect('/details')

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format!")
        return redirect('/details')
        # Store details in session
    session['user_details'] = {
        'name': name,
        'email': email,
        'phone': phone,
        'address': address
    }
    # If all validations pass, redirect to the payment page
    return redirect('/payments')
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


def get_current_time():
    now_utc = datetime.now(timezone.utc)
    # IST is UTC + 5:30
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset
    return now_ist.date(), now_ist.time()

# Add a new route to handle payment completion
@app.route('/complete_payment', methods=['POST'])
def complete_payment():
    current_date, current_time = get_current_time()
    try:
        registration_data = session.get('registration_data')
        user_details = session.get('user_details')
        if not registration_data or not user_details:
            flash("No registration or user details data found!", "danger")
            return redirect(url_for('home'))
        # Create new user with the stored registration data
        new_user = DogDetails(
            name=registration_data['name'],
            breed=registration_data['breed'],
            age=registration_data['age'],
            event=registration_data['event']
        )
        db.session.add(new_user)
        db.session.commit()
        # Create user details record
        new_user_details = UserDetails(
            user_id=new_user.id,
            name=user_details['name'],
            email=user_details['email'],
            phone=user_details['phone'],
            address=user_details['address'],
            created_date=current_date,
            created_time=current_time
        )
        
        db.session.add(new_user_details)
        db.session.commit()
        
        
        # Clear the session data
        session.pop('registration_data', None)
        session.pop('user_details', None)
        flash("Registration and payment completed successfully!", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during payment completion: {e}")
        flash("Error completing registration", "danger")
        return redirect(url_for('payments'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    service_id = request.args.get('service_id')
    service = Competition.query.get(service_id)

    if not service:
        flash("Service not found!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            breed = request.form.get('breed')
            age = request.form.get('age')
            event = service.title

            if not all([name, breed, age]):
                flash("All fields are required!", "danger")
                return render_template('register.html', service=service)

            try:
                age = int(age)
                if age < 0:
                    raise ValueError("Age must be positive")
            except ValueError as e:
                flash(f"Invalid age: {str(e)}", "danger")
                return render_template('register.html', service=service)

            # Store registration data in session instead of database
            session['registration_data'] = {
                'name': name,
                'breed': breed,
                'age': age,
                'event': event
            }
            
            return redirect(url_for('details'))

        except Exception as e:
            logger.error(f"Error during registration process: {e}")
            flash(f"Error: {str(e)}", "danger")
            return render_template('register.html', service=service)

    return render_template('register.html', service=service)

if __name__ == '__main__':
    app.run(debug=True)