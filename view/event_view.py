class EventView:
    """Vue pour la gestion des événements."""

    def display_info_message(self, message):
        """Affiche un message d'information."""
        print(f"ℹ️ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")

    def input_event_info(self):
        """Demande à l'utilisateur de saisir les informations de l'événement."""

        name = input("📅 Nom de l'événement : ").strip()
        start_date = input("📆 Date de début (YYYY-MM-DD HH:MM) : ").strip()
        end_date = input("📆 Date de fin (YYYY-MM-DD HH:MM) : ").strip()
        location = input("📍 Lieu : ").strip()
        attendees = input("👥 Nombre de participants : ").strip()
        support_id = input("📋 ID du support : ").strip()
        notes = input("📝 Notes (facultatif) : ").strip()

        return (
            name,
            start_date,
            end_date,
            location,
            int(attendees),
            support_id if support_id else None,
            notes if notes else None,
        )

    def display_events(self, events):
        """Affiche une liste d'événements."""
        print("Liste des événements :")
        for event in events:
            print(
                f"📅 {event.name} ({event.start_date} - {event.end_date}) - {event.location} - {event.attendees} participants -{event.notes} "
            )
        print("\n")
