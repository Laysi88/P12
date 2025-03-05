from model.contrat import Contrat
from model.client import Client
from controller.base_controller import BaseController
from utils.config import Session as DBSession
from view.contrat_view import ContratView
import sentry_sdk


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
        result = self.view.input_contrat_info(clients)
        if result is None:
            return
        client_id, total_amount, remaining_amount = result
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

        sentry_sdk.capture_message(f"Contrat créé pour {client.name}.", level="info")

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

        sentry_sdk.capture_message(f"Contrat {contrat.id} mis à jour.", level="info")

        self.view.display_info_message(f"✅ Contrat {contrat.id} mis à jour avec succès !")
        return contrat

    def read_contrat(self):
        """Affiche tous les contrats si l'utilisateur a la permission."""

        if not self.check_permission("read_contrat"):
            self.view.display_error_message("❌ Accès refusé : Vous n'avez pas la permission d'afficher les contrats.")
            return []

        contrats = self.session.query(Contrat).all()

        if not contrats:
            self.view.display_info_message("📭 Aucun contrat trouvé.")
        else:
            self.view.display_contrats(contrats)

        return contrats

    def filter_contrats(self):
        """Permet à l'utilisateur de filtrer les contrats (non signés ou avec paiement en attente)."""

        if not self.check_permission("filter_contrat"):
            self.view.display_error_message("❌ Accès refusé : Vous n'avez pas la permission d'afficher les contrats.")
            return []

        filtre = self.view.ask_filter_option()

        query = self.session.query(Contrat)

        if filtre == "non_signes":
            query = query.filter_by(status=False)
        elif filtre == "paiement_en_attente":
            query = query.filter(Contrat.remaining_amount > 0)
        else:
            self.view.display_error_message("❌ Option invalide.")
            return []

        contrats = query.all()

        if not contrats:
            self.view.display_info_message("📭 Aucun contrat trouvé pour ce filtre.")
        else:
            self.view.display_contrats(contrats)

        return contrats
