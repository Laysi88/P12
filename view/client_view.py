class ClientView:
    """Vue pour gérer l'affichage des clients et les interactions utilisateur."""

    def input_client_info(self):
        """Demande à l'utilisateur de saisir les informations du client."""
        print("\n📝 Création d'un nouveau client :")
        name = input("🔹 Nom du client : ").strip()
        email = input("📧 Email : ").strip()
        phone = input("📞 Téléphone : ").strip()
        company = input("🏢 Entreprise : ").strip()
        return name, email, phone, company

    def display_info_message(self, message):
        """Affiche un message d'information."""
        print(f"ℹ️ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")

    def display_clients(self, clients):
        """Affiche une liste de clients."""
        if not clients:
            print("\n📜 Aucun client à afficher.")
        else:
            print("\n📜 Liste des clients :")
            for client in clients:
                print(f"- {client.id}: {client.name} ({client.email}) - Entreprise: {client.company}")
            return

    def display_client_details(self, client):
        """Affiche les détails d'un client."""
        print("\n👤 Détails du client :")
        print(f"🔹 ID : {client.id}")
        print(f"🔹 Nom : {client.name}")
        print(f"🔹 Email : {client.email}")
        print(f"🔹 Téléphone : {client.phone}")
        print(f"🔹 Entreprise : {client.company}")
        commercial_name = client.commercial.name if client.commercial else "Non attribué"
        print(f"🔹 Commercial : {commercial_name}")
