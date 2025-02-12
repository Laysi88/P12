from sqlalchemy.exc import SQLAlchemyError
from model.role import Role
from model.user import User
from sqlalchemy.orm import Session


def seed_admin_user(session: Session):
    """Ajoute un administrateur par défaut s'il n'existe pas."""
    admin_email = "admin@admin.com"
    admin_name = "Admin"
    admin_password = "admin123"

    try:
        existing_admin = session.query(User).filter_by(email=admin_email).first()

        if not existing_admin:
            admin_role = session.query(Role).filter_by(name="gestion").first()
            if not admin_role:
                print("⚠️ Aucun rôle 'gestion' trouvé. Création annulée.")
                return
            admin_user = User(name=admin_name, email=admin_email, password=admin_password, role_id=admin_role.id)

            session.add(admin_user)
            session.commit()
            print(f"✅ Administrateur ajouté : {admin_email}")

    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Erreur lors de l'insertion de l'admin :", e)


def seed_roles(session: Session):
    """Ajoute les rôles s'ils n'existent pas encore."""
    roles = ["support", "commercial", "gestion"]

    try:
        existing_roles = {role.name for role in session.query(Role).all()}
        new_roles = [Role(name=role) for role in roles if role not in existing_roles]

        if new_roles:
            session.add_all(new_roles)
            session.commit()
            print("Rôles ajoutés :", [role.name for role in new_roles])
        else:
            print("Tous les rôles existent déjà.")

    except SQLAlchemyError as e:
        session.rollback()
        print("Erreur lors de l'insertion des rôles :", e)
