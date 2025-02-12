import sys
from controller.auth_controller import AuthController
from controller.user_controller import UserController
from utils.populate_database import seed_admin_user, seed_roles
from utils.config import Session
from model.role import Role
from model.user import User


def initialize_database():
    """Ajoute les rôles et l'admin s'ils n'existent pas encore."""
    session = Session()
    if session.query(Role).count() == 0:
        print("📌 Création des rôles...")
        seed_roles(session)
    admin_exists = (
        session.query(User).join(Role).filter(User.email == "admin@admin.com", Role.name == "gestion").first()
    )

    if admin_exists is None:
        print("📌 Création de l'admin par défaut...")
        seed_admin_user(session)

    session.close()


def main():
    auth_controller = AuthController()

    if len(sys.argv) > 1 and sys.argv[1] == "login":
        auth_controller.login()
        return

    user = auth_controller.verify_token()
    if not user:
        print("\n🔐 Connectez-vous d'abord avec `python epicevents.py login`")
        return

    user_controller = UserController(user)

    while True:
        print("\n--- Menu CRM EPICEVENT ---")
        print("1️⃣ - Créer un utilisateur")
        print("2️⃣ - Lister les utilisateurs")
        print("3️⃣ - Supprimer un utilisateur")
        print("4️⃣ - Se déconnecter")
        print("5️⃣ - Quitter")

        choix = input("👉 Faites votre choix : ")

        if choix == "1":
            user_controller.create_user()
        elif choix == "2":
            user_controller.list_users()
        elif choix == "3":
            user_id = int(input("ID de l'utilisateur à supprimer : "))
            user_controller.delete_user(user_id)
        elif choix == "4":
            auth_controller.logout()
            break
        elif choix == "5":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide, veuillez recommencer.")


if __name__ == "__main__":
    initialize_database()
    main()
