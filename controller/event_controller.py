from controller.base_controller import BaseController
from model.event import Event
from model.contrat import Contrat
from view.event_view import EventView
from utils.config import Session as DBSession


class EventController(BaseController):
    def __init__(self, user):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        super().__init__(user, DBSession())
        self.model = Event
        self.view = EventView()

    def create_event(self):
        """Création d'un événement (réservé aux commerciaux)."""

        if not self.check_permission("create_event"):
            self.view.display_error_message("❌ Accès refusé : Vous ne pouvez pas créer un événement.")
            return None

        contrats = self.session.query(Contrat).filter_by(status=True).all()

        if not contrats:
            self.view.display_error_message("⚠️ Aucun contrat signé disponible pour créer un événement.")
            return None

        contrat_id, name, start_date, end_date, location, attendees, support_id, notes = self.view.input_event_info(
            contrats
        )
        contrat = self.session.query(Contrat).filter_by(id=contrat_id).first()
        if not contrat:
            self.view.display_error_message("⚠️ Contrat inexistant.")
            return None

        new_event = Event(
            name=name,
            contrat_id=contrat_id,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
            support_id=support_id,
            notes=notes,
        )

        self.session.add(new_event)
        self.session.commit()
        self.view.display_info_message(f"✅ Événement '{name}' créé avec succès pour le contrat {contrat_id} !")
        return new_event
