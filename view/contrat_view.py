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

        user_input = input("\n🆔 Entrez l'ID du client (ou appuyez sur Entrée pour annuler) : ").strip()

        if not user_input:  # ➜ Si vide, on annule immédiatement
            print("🔙 Retour au menu précédent.")
            return None

        if not user_input.isdigit() or int(user_input) not in [c.id for c in clients]:
            print("❌ ID invalide.")
            return None  # ➜ Quitte immédiatement en cas d'ID invalide

        client_id = int(user_input)

        try:
            total_amount = float(input("💰 Montant total (€) : ").strip())
            remaining_amount = float(input("💰 Montant restant (€) : ").strip())
            return client_id, total_amount, remaining_amount
        except ValueError:
            print("❌ Montant invalide.")
            return None

    def input_update_contrat_info(self, contrat):
        """Demande à l'utilisateur de saisir les nouvelles infos du contrat."""

        print(f"\n🔄 Mise à jour du contrat {contrat.id} ({contrat.client.name})")
        print(f"💰 Montant total actuel : {contrat.total_amount}")
        print(f"💰 Montant restant actuel : {contrat.remaining_amount}")
        print(f"📜 Statut actuel : {'✅ Signé' if contrat.status else '❌ Non signé'}")

        new_total_amount = None
        new_status = contrat.status  # ✅ Ajout d'une valeur par défaut !

        if not contrat.status:
            new_status = input("✍️ Signer le contrat ? (oui/non, laisser vide pour ne pas changer) : ").strip().lower()
            new_status = True if new_status == "oui" else contrat.status

            new_total_amount = input("💰 Nouveau montant total (laisser vide pour ne pas changer) : ").strip()
            new_total_amount = float(new_total_amount) if new_total_amount else contrat.total_amount

        new_remaining_amount = input("💰 Nouveau montant restant (laisser vide pour ne pas changer) : ").strip()
        new_remaining_amount = float(new_remaining_amount) if new_remaining_amount else contrat.remaining_amount

        return new_total_amount, new_remaining_amount, new_status

    def display_contrats(self, contrats):
        """Affiche une liste de contrats."""
        if not contrats:
            print("📭 Aucun contrat à afficher.")
            return

        print("\n📜 Liste des contrats :")
        for contrat in contrats:
            print(
                f"🔹 ID: {contrat.id} | Client: {contrat.client.name} | Total: {contrat.total_amount}€ "
                f"| Restant: {contrat.remaining_amount}€ | Signé: {'✅ Oui' if contrat.status else '❌ Non'}"
            )

    def ask_filter_option(self):
        """Demande à l'utilisateur quel type de filtrage il veut appliquer."""
        print("\n📌 Choisissez un filtre pour afficher les contrats :")
        print("1️⃣ - Contrats non signés")
        print("2️⃣ - Contrats non entièrement payés")

        choix = input("👉 Entrez votre choix (1 ou 2) : ").strip()

        if choix == "1":
            return "non_signes"
        elif choix == "2":
            return "paiement_en_attente"
        else:
            return None
