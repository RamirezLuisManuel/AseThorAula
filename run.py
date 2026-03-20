from app import create_app, db
from app.models import User, Profile, TutoringSession, Enrollment, Review

app = create_app()

with app.app_context():
    db.create_all()
    
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Profile': Profile, 'TutoringSession': TutoringSession, 'Enrollment': Enrollment, 'Review': Review}

if __name__ == '__main__':
    app.run(debug=True)
