from model.client import Client
from view.client_view import ClientView
from controller.base_controller import BaseController
from utils.config import Session as DBSession


class ClientController(BaseController):
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        super().__init__(user, DBSession())
        self.model = Client
        self.view = ClientView()

    def create_client(self):
        """Création d'un nouveau client (réservé aux commerciaux)."""

        if not self.check_permission("create_client"):
            self.view.display_error_message("❌ Accès refusé : Seuls les commerciaux peuvent créer des clients.")
            return None

        name, email, phone, company = self.view.input_client_info()
        existing_client = self.session.query(Client).filter_by(email=email).first()
        if existing_client:
            self.view.display_error_message("⚠️ Un client avec cet email existe déjà.")
            return None

        new_client = self.model(
            name=name,
            email=email,
            phone=phone,
            company=company,
            commercial_id=self.user.id,
        )

        self.session.add(new_client)
        self.session.commit()

        self.view.display_info_message(f"✅ Client '{name}' créé et attribué à {self.user.name}.")
        return new_client

    def list_all_client(self):
        """Liste tous les clients (réservé aux commerciaux)."""
        if not self.check_permission("read_client"):
            self.view.display_error_message("❌ Accès refusé : Seuls les commerciaux peuvent lire les clients.")
            return None

        clients = self.session.query(Client).all()
        self.view.display_clients(clients)
        return clients

    def list_personnal_client(self):
        """Liste les clients personnels (réservé aux commerciaux)."""
        if not self.check_permission("read_client"):
            self.view.display_error_message("❌ Accès refusé : Seuls les commerciaux peuvent lire les clients.")
            return None

        clients = self.session.query(Client).filter_by(commercial_id=self.user.id).all()
        self.view.display_clients(clients)
        return clients

    def update_client(self, client_id):
        """Mise à jour des informations d'un client (nécessite 'update_client')."""

        if not self.check_permission("update_client"):
            return None

        client = self.session.query(Client).filter_by(id=client_id).first()
        if not client:
            self.view.display_error_message("⚠️ Client inexistant.")  # ✅ Correction ici
            return None

        name, email, phone, company = self.view.input_client_info()

        existing_client = self.session.query(Client).filter(Client.email == email, Client.id != client_id).first()
        if existing_client:
            self.view.display_error_message("⚠️ Email déjà utilisé.")  # ✅ Correction ici
            return None

        client.name = name if name else client.name
        client.email = email if email else client.email
        client.phone = phone if phone else client.phone
        client.company = company if company else client.company

        self.session.commit()
        self.view.display_info_message(f"✅ Client {client_id} mis à jour !")
