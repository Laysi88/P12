from controller.base_controller import BaseController
from model.event import Event
from model.contrat import Contrat
from view.event_view import EventView
from utils.config import Session as DBSession
import sentry_sdk


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
        sentry_sdk.capture_message(
            f"📅 Nouvel événement créé : {new_event.name} ({new_event.start_date} - {new_event.end_date})",
            level="info",
        )
        self.view.display_info_message(f"✅ Événement '{name}' créé avec succès pour le contrat {contrat_id} !")
        return new_event

    def read_event(self):
        """Lecture de tous les événements."""

        if not self.check_permission("read_event"):
            self.view.display_error_message("❌ Accès refusé : Vous ne pouvez pas lire un événement.")
            return []

        events = self.session.query(Event).all()

        if not events:
            self.view.display_info_message("📭 Aucun événement disponible.")
        else:
            self.view.display_events(events)

        return events

    def filter_event(self):
        """Filtrer les événements selon le rôle (support ou gestion)."""

        if not self.check_permission("filter_event"):
            self.view.display_error_message("❌ Accès refusé : Vous ne pouvez pas filtrer les événements.")
            return []

        events = []

        if self.user.role.name == "support":
            events = self.session.query(Event).filter_by(support_id=self.user.id).all()
        if self.user.role.name == "gestion":
            events = self.session.query(Event).filter_by(support_id=None).all()

        if not events:
            self.view.display_info_message("📭 Aucun événement trouvé pour ce filtre.")
        else:
            self.view.display_events(events)

        return events

    def update_event(self, event_id):
        """Met à jour un événement (gestion attribue un support, support met à jour les notes)."""

        if not self.check_permission("update_event"):
            self.view.display_error_message("❌ Accès refusé : Vous ne pouvez pas modifier cet événement.")
            return None

        event = self.session.query(Event).filter_by(id=event_id).first()

        if not event:
            self.view.display_error_message("⚠️ Événement inexistant.")
            return None

        if self.user.role.name == "gestion":
            new_support_id = self.view.input_support_assignment()
            event.support_id = new_support_id

        if self.user.role.name == "support":
            new_notes = self.view.input_update_notes()
            event.notes = new_notes

        self.session.commit()
        sentry_sdk.capture_message(
            f"📅 Événement mis à jour : {event.name} ({event.start_date} - {event.end_date})", level="info"
        )
        self.view.display_info_message(f"✅ Événement {event.id} mis à jour avec succès !")
        return event
