from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import csv
import io
from app import db
from app.models import User, Result
from app.forms import LoginForm, UploadForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page redirects to login."""
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both students and admins."""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.student_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            
            if user.is_admin():
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/admin/dashboard', methods=['GET', 'POST'])  # Add POST method
@login_required
def admin_dashboard():
    """Admin dashboard."""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.student_dashboard'))
    
    form = UploadForm()  # Create form instance
    
    # Handle form submission
    if form.validate_on_submit():
        return handle_csv_upload(form)
    
    # Get stats for dashboard
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_results = Result.query.count()
    
    return render_template('admin_dashboard.html', 
                         form=form,
                         total_users=total_users,
                         total_students=total_students,
                         total_results=total_results)

def handle_csv_upload(form):
    """Handle CSV file upload and processing."""
    try:
        csv_file = form.csv_file.data
        if not csv_file:
            flash('No file selected', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Read and parse CSV
        stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        required_columns = ['student_id', 'student_name', 'subject', 'marks']
        if not all(col in csv_reader.fieldnames for col in required_columns):
            flash(f'CSV must contain columns: {", ".join(required_columns)}', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        processed_count = 0
        error_count = 0
        created_students = []
        created_results = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 because of header
            try:
                csv_student_id = int(row['student_id'])
                marks = int(row['marks'])
                student_name = row['student_name']
                subject = row['subject']
                
                # Validate marks
                if marks < 0 or marks > 100:
                    error_count += 1
                    current_app.logger.warning(f"Row {row_num}: Invalid marks {marks}")
                    continue
                
                # Check if student exists - look by CSV student_id
                student = User.query.filter_by(id=csv_student_id, role='student').first()
                
                if not student:
                    # Check if ID is taken by non-student user
                    existing_user = User.query.get(csv_student_id)
                    if existing_user:
                        # ID conflict - find next available ID
                        max_id = db.session.query(db.func.max(User.id)).scalar() or 0
                        new_student_id = max_id + 1
                        student = User(
                            id=new_student_id,
                            username=f"student{new_student_id}",
                            email=f"student{new_student_id}@school.edu",
                            role='student'
                        )
                        flash(f"Student ID {csv_student_id} was taken, assigned new ID: {new_student_id}", 'warning')
                    else:
                        # Use the CSV student_id
                        student = User(
                            id=csv_student_id,
                            username=f"student{csv_student_id}",
                            email=f"student{csv_student_id}@school.edu",
                            role='student'
                        )
                    
                    student.set_password(f"student{student.id}")
                    db.session.add(student)
                    created_students.append(student_name)
                    print(f"✅ Created new student: {student_name} (ID: {student.id})")
                
                # Create or update result
                result = Result.query.filter_by(
                    student_id=student.id, 
                    subject=subject
                ).first()
                
                if result:
                    result.marks = marks
                    action = "updated"
                else:
                    result = Result(
                        student_id=student.id,
                        subject=subject,
                        marks=marks
                    )
                    db.session.add(result)
                    action = "created"
                    created_results.append(f"{student_name} - {subject}")
                
                processed_count += 1
                current_app.logger.info(f"Row {row_num}: {action} result for {student_name} - {subject}: {marks}")
                
            except (ValueError, KeyError) as e:
                error_count += 1
                current_app.logger.error(f"Row {row_num}: Error {e} with data {row}")
                continue
        
        db.session.commit()
        
        # Prepare success message
        success_message = f'✅ Successfully processed {processed_count} records!'
        
        if created_students:
            unique_students = list(set(created_students))
            success_message += f' Created {len(unique_students)} new student accounts.'
        
        if error_count > 0:
            success_message += f' {error_count} errors occurred.'
            
        flash(success_message, 'success')
        
        # Log details
        if created_students:
            print(f"🎓 New students created: {', '.join(set(created_students))}")
        if created_results:
            print(f"📚 New results created: {len(created_results)}")
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {e}")
        flash(f'❌ Error processing file: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard showing their results."""
    if current_user.is_admin():
        return redirect(url_for('main.admin_dashboard'))
    
    results = Result.query.filter_by(student_id=current_user.id).all()
    
    # Calculate average if there are results
    average = None
    if results:
        total_marks = sum(result.marks for result in results)
        average = total_marks / len(results)
    
    return render_template('student_dashboard.html', results=results, average=average)