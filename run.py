from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add models to Flask shell context."""
    return {'db': db, 'User': User, 'Result': Result}

def init_demo_data():
    """Initialize demo data for development."""
    with app.app_context():
        # Create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@school.edu',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user: admin / admin123")
        
        # Create demo student
        student = User.query.filter_by(username='student1').first()
        if not student:
            student = User(
                username='student1',
                email='student1@school.edu',
                role='student'
            )
            student.set_password('student1')
            db.session.add(student)
            print("Created student user: student1 / student1")
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_demo_data()
    app.run(debug=True)