from model.contrat import Contrat
from model.client import Client
from controller.base_controller import BaseController
from utils.config import Session as DBSession
from view.contrat_view import ContratView


class ContratController(BaseController):
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        super().__init__(user, DBSession())
        self.model = Contrat
        self.view = ContratView()

    def create_contrat(self):
        """Création d'un contrat (réservé aux commerciaux gérant le client et aux gestionnaires)."""

        if not self.check_permission("create_contrat"):
            self.view.display_error_message(
                "❌ Accès refusé : Seuls les commerciaux (gérant le client) et les gestionnaires peuvent créer un contrat."
            )
            return None
        if self.user.role.name == "commercial":
            clients = self.session.query(Client).filter_by(commercial_id=self.user.id).all()
        else:
            clients = self.session.query(Client).all()

        if not clients:
            self.view.display_error_message("⚠️ Aucun client disponible.")
            return None
        client_id, total_amount, remaining_amount = self.view.input_contrat_info(clients)
        client = self.session.query(Client).filter_by(id=client_id).first()
        if not client:
            self.view.display_error_message("⚠️ Client inexistant.")
            return None
        if self.user.role.name == "commercial" and client.commercial_id != self.user.id:
            self.view.display_error_message("⚠️ Vous ne pouvez créer un contrat que pour vos propres clients.")
            return None
        new_contrat = Contrat(
            client_id=client_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            status=False,
        )
        self.session.add(new_contrat)
        self.session.commit()
        self.view.display_info_message(f"✅ Contrat créé avec succès pour le client {client.name} !")
        return new_contrat

    def update_contrat(self, contrat_id):
        """Met à jour un contrat (total_amount modifiable avant signature, remaining_amount toujours modifiable, signature possible)."""

        if not self.check_permission("update_contrat"):
            self.view.display_error_message("❌ Accès refusé : Vous ne pouvez pas modifier ce contrat.")
            return None

        contrat = self.session.query(Contrat).filter_by(id=contrat_id).first()

        if not contrat:
            self.view.display_error_message("⚠️ Contrat inexistant.")
            return None

        if self.user.role.name == "commercial" and contrat.client.commercial_id != self.user.id:
            self.view.display_error_message("⚠️ Vous ne pouvez modifier que les contrats de vos propres clients.")
            return None

        new_total_amount, new_remaining_amount, new_status = self.view.input_update_contrat_info(contrat)

        if not contrat.status:
            contrat.total_amount = new_total_amount
        contrat.remaining_amount = new_remaining_amount
        contrat.status = new_status

        self.session.commit()
        self.view.display_info_message(f"✅ Contrat {contrat.id} mis à jour avec succès !")
        return contrat
