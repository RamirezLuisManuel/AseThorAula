from app import create_app, db, bcrypt
from app.models import User, Profile

app = create_app()

with app.app_context():
    db.create_all()
    
    # Check if Super-Admin exists
    super_admin = User.query.filter_by(role='Super-Admin').first()
    if not super_admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='superadmin', password_hash=hashed_password, role='Super-Admin')
        db.session.add(admin_user)
        db.session.commit()
        
        # Add a default profile
        admin_profile = Profile(user_id=admin_user.id, full_name='Super Administrador', bio='Administrador principal del sistema.')
        db.session.add(admin_profile)
        db.session.commit()
        print("Base de datos inicializada. Usuario Super-Admin creado (username: superadmin, password: admin123).")
    else:
        print("La base de datos ya está inicializada. Super-Admin encontrado.")
