from model.client import Client
from view.client_view import ClientView
from controller.base_controller import BaseController
from utils.config import Session as DBSession
from datetime import datetime


class ClientController(BaseController):
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        self.session = DBSession()
        super().__init__(user, self.session)
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
            date_created=datetime.now(),
            date_updated=datetime.now(),
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
