from sqlalchemy.exc import SQLAlchemyError
from model.role import Role
from sqlalchemy.orm import Session


# création des roles dans la base de données
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
