from utils.config import Session as DBSession
from model.user import User
from model.role import Role
from view.user_view import UserView


class UserController:
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        self.session = DBSession()
        self.model = User
        self.view = UserView()
        self.user = user

    def check_permission(self, action):
        """Vérifie si l'utilisateur connecté a la permission d'effectuer une action."""
        print(f"🔍 Vérification permission : action={action}, rôle={self.user.role.name if self.user.role else None}")
        if self.user.role and self.user.role.has_permission(action):
            print("✅ Permission accordée")
            return True
        else:
            print("⛔ Permission refusée")
            self.view.display_error_message(f"⛔ Accès refusé : Vous n'avez pas la permission '{action}'.")
            return False

    def create_user(self):
        """Création d'un nouvel utilisateur (nécessite 'create_user')."""
        if not self.check_permission("create_user"):
            return None

        name, email, password = self.view.input_infos_user()
        role_name = self.view.choose_role()

        role = self.session.query(Role).filter_by(name=role_name).first()
        if not role:
            self.view.display_error_message("❌ Rôle invalide !")
            return None

        # Correction : Passer role_id au lieu de role
        new_user = self.model(name=name, email=email, password=password, role_id=role.id)
        self.session.add(new_user)
        self.session.commit()
        self.view.display_info_message(f"✅ Utilisateur '{name}' créé avec succès !")
        return new_user

    def delete_user(self, user_id):
        """Suppression d'un utilisateur (nécessite 'delete_user')."""
        if not self.check_permission("delete_user"):
            return None

        user_to_delete = self.session.query(User).filter_by(id=user_id).first()
        if user_to_delete:
            self.session.delete(user_to_delete)
            self.session.commit()
            self.view.display_info_message(f"✅ Utilisateur {user_id} supprimé !")
        else:
            self.view.display_error_message(f"⚠️ L'utilisateur {user_id} n'existe pas.")

    def list_users(self):
        """Affichage de la liste des utilisateurs (nécessite 'read_user')."""
        if not self.check_permission("read_user"):
            return None

        users = self.session.query(User).all()
        self.view.display_users(users)

    def get_user_details(self, user_id):
        """Affiche les détails d'un utilisateur spécifique (nécessite 'read_user')."""
        if not self.check_permission("read_user"):
            return None

        user = self.session.query(User).filter_by(id=user_id).first()
        if user:
            self.view.display_user_details(user)
        else:
            self.view.display_error_message(f"⚠️ L'utilisateur {user_id} n'existe pas.")

    def assign_client_to_user(self, user_id, client):
        """Assigne un client à un utilisateur (commercial uniquement)."""
        if not self.check_permission("assign_client"):
            return None

        user = self.session.query(User).filter_by(id=user_id).first()
        if user and user.role.name == "commercial":
            user.clients.append(client)
            self.session.commit()
            self.view.display_info_message(f"✅ Client '{client.name}' assigné à {user.name}")
        else:
            self.view.display_error_message("❌ Impossible d'assigner un client à cet utilisateur.")
