class ContratView:
    def display_info_message(self, message):
        """Affiche un message d'information."""
        print(f"ℹ️ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")

    def input_contrat_info(self, clients):
        """Demande à l'utilisateur de saisir les informations du contrat."""

        print("\n📜 Clients disponibles :")
        for client in clients:
            print(f"- {client.id}: {client.name} ({client.email})")

        while True:
            try:
                client_id = int(input("\n🆔 Entrez l'ID du client : ").strip())
                if any(client.id == client_id for client in clients):
                    break
                else:
                    print("❌ ID invalide. Veuillez entrer un ID existant.")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")

        total_amount = float(input("💰 Montant total (€) : ").strip())
        remaining_amount = float(input("💰 Montant restant (€) : ").strip())

        return client_id, total_amount, remaining_amount
