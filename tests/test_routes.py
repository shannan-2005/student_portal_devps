import pytest
import io
import csv
from app import create_app, db
from app.models import User, Result

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def init_database(app):
    """Initialize the database with test data."""
    with app.app_context():
        # Create admin user
        admin = User(username='admin', email='admin@school.edu', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create student user
        student = User(username='student1', email='student1@school.edu', role='student')
        student.set_password('student1')
        db.session.add(student)
        
        # Create some results
        result1 = Result(student_id=student.id, subject='Mathematics', marks=85)
        result2 = Result(student_id=student.id, subject='Science', marks=92)
        db.session.add_all([result1, result2])
        
        db.session.commit()
    
    return db

def test_student_login_success(client, init_database):
    """Test successful student login."""
    response = client.post('/login', data={
        'username': 'student1',
        'password': 'student1'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'My Academic Results' in response.data

def test_admin_login_success(client, init_database):
    """Test successful admin login."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_login_failure(client, init_database):
    """Test login with wrong credentials."""
    response = client.post('/login', data={
        'username': 'student1',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_csv_processing_logic(app, init_database):
    """Test CSV processing logic."""
    with app.app_context():
        # Create test CSV data
        csv_data = [
            ['student_id', 'student_name', 'subject', 'marks'],
            ['2', 'Jane Smith', 'Mathematics', '78'],
            ['2', 'Jane Smith', 'Science', '85'],
            ['3', 'Bob Johnson', 'Mathematics', '92']
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        csv_string = output.getvalue()
        
        # Test the CSV processing (simulating the route logic)
        from app.routes import process_csv_data
        processed, errors = process_csv_data(csv_string)
        
        assert processed == 3
        assert errors == 0
        
        # Verify data was saved
        student2 = User.query.filter_by(id=2).first()
        assert student2 is not None
        assert student2.role == 'student'
        
        results = Result.query.filter_by(student_id=2).all()
        assert len(results) == 2

def test_student_access_admin_dashboard(client, init_database):
    """Test that students cannot access admin dashboard."""
    # Login as student
    client.post('/login', data={
        'username': 'student1',
        'password': 'student1'
    })
    
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert b'Access denied' in response.data
    assert b'My Academic Results' in response.data  # Redirected to student dashboard

def test_admin_access_student_dashboard(client, init_database):
    """Test that admins are redirected from student dashboard."""
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.get('/student/dashboard', follow_redirects=True)
    assert b'Admin Dashboard' in response.data  # Redirected to admin dashboard

# Helper function for CSV processing (add this to routes.py)
def process_csv_data(csv_string):
    """Helper function to process CSV data for testing."""
    from app import db
    from app.models import User, Result
    import csv
    import io
    
    stream = io.StringIO(csv_string)
    csv_reader = csv.DictReader(stream)
    
    processed_count = 0
    error_count = 0
    
    for row in csv_reader:
        try:
            student_id = int(row['student_id'])
            marks = int(row['marks'])
            
            student = User.query.filter_by(id=student_id, role='student').first()
            if not student:
                student = User(
                    id=student_id,
                    username=f"student{student_id}",
                    email=f"student{student_id}@school.edu",
                    role='student'
                )
                student.set_password(f"student{student_id}")
                db.session.add(student)
            
            result = Result.query.filter_by(
                student_id=student_id, 
                subject=row['subject']
            ).first()
            
            if result:
                result.marks = marks
            else:
                result = Result(
                    student_id=student_id,
                    subject=row['subject'],
                    marks=marks
                )
                db.session.add(result)
            
            processed_count += 1
            
        except (ValueError, KeyError):
            error_count += 1
            continue
    
    db.session.commit()
    return processed_count, error_count