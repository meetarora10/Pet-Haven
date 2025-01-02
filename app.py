# app.py
from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///infy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    event = db.Column(db.String(100), nullable=False)
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)


with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        
        if not Service.query.first():
            services = [
                Service(title="Agility Challenge", date="24-03-2025", time="10:00 am", 
                       description="Test your dog's ability to complete an obstacle course following the commands."),
                Service(title="Obedience Trial", date="25-03-2025", time="12:00 am", 
                       description="Dog and handler perform a series of obedience exercises to demonstrate their training."),
                Service(title="Best Costume Show", date="26-03-2025", time="12:00 am", 
                       description="Elegant Tails, Happy Hearts"),  
            ]
            db.session.add_all(services)
            db.session.commit()
            logger.info("Initial services added successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

@app.route('/')
def home():
    services = Service.query.all()
    return render_template('index.html', services=services)

@app.route('/admin')
def admin():
    services = Service.query.all()
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
        registrations = db.session.query(User).all()
        
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

            # Validate required fields
            if not all([title, date, time, description]):
                flash("All fields are required!", "danger")
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

            # Create new service
            new_competition = Service(
                title=title,
                date=formatted_date,
                time=formatted_time,
                description=description
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
        service = Service.query.get_or_404(service_id)
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
        service = Service.query.get_or_404(service_id)
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('competition_name')
            date = request.form.get('date')
            time = request.form.get('time')
            description = request.form.get('description')
            capacity = request.form.get('capacity')

            # Validate form data
            errors = validate_service_data(title, date, time, description)
            
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

@app.route('/myevents')
def myevents():
    try:
        latest_registration = db.session.query(User).order_by(User.id.desc()).first()

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

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    service_id = request.args.get('service_id')
    service = Service.query.get(service_id)

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
            
            return redirect(url_for('payments'))

        except Exception as e:
            logger.error(f"Error during registration process: {e}")
            flash(f"Error: {str(e)}", "danger")
            return render_template('register.html', service=service)

    return render_template('register.html', service=service)

# Add a new route to handle payment completion
@app.route('/complete_payment', methods=['POST'])
def complete_payment():
    try:
        registration_data = session.get('registration_data')
        
        if not registration_data:
            flash("No registration data found!", "danger")
            return redirect(url_for('home'))
        
        # Create new user with the stored registration data
        new_user = User(
            name=registration_data['name'],
            breed=registration_data['breed'],
            age=registration_data['age'],
            event=registration_data['event']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Clear the session data
        session.pop('registration_data', None)
        
        flash("Registration and payment completed successfully!", "success")
        return redirect(url_for('myevents'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during payment completion: {e}")
        flash("Error completing registration", "danger")
        return redirect(url_for('payments'))
if __name__ == '__main__':
    app.run(debug=True)