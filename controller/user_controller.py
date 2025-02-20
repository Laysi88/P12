from utils.config import Session as DBSession
from model.user import User
from model.role import Role
from view.user_view import UserView
from controller.base_controller import BaseController


class UserController(BaseController):
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        super().__init__(user, DBSession())
        self.model = User
        self.view = UserView()

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

    def update_user(self, user_id):
        """Mise à jour des informations d'un utilisateur (nécessite 'update_user')."""

        if not self.check_permission("update_user"):
            return None
        user = self.session.query(User).filter_by(id=user_id).first()
        if not user:
            self.view.display_error_message(f"⚠️ L'utilisateur {user_id} n'existe pas.")
            return None
        name, email, password = self.view.input_infos_user()
        existing_user = self.session.query(User).filter(User.email == email, User.id != user_id).first()
        if existing_user:
            self.view.display_error_message("❌ Cet email est déjà utilisé !")
            return None
        user.name = name if name else user.name
        user.email = email if email else user.email
        if password:
            user.password = user.set_password(password)
        self.session.commit()
        self.view.display_info_message(f"✅ Utilisateur {user_id} mis à jour !")
