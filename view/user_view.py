class UserView:
    def input_infos_user(self):
        """Demande à l'utilisateur de saisir les informations nécessaires pour la création d'un compte."""
        name = input("Nom : ")
        email = input("Email : ")
        password = input("Mot de passe : ")
        return name, email, password

    def choose_role(self):
        """Demande à l'utilisateur de choisir un rôle valide."""
        print("Rôles disponibles : [gestion, commercial, support]")
        return input("👉 Choisissez un rôle : ")

    def display_users(self, users):
        """Affiche la liste des utilisateurs."""
        print("\n📜 Liste des utilisateurs :")
        for user in users:
            role_name = user.role.name if user.role else "Aucun rôle"
            print(f"- {user.id}: {user.name} ({user.email}) - Rôle: {role_name}")

    def display_user_details(self, user):
        """Affiche les détails d'un utilisateur spécifique."""
        role_name = user.role.name if user.role else "Aucun rôle"
        print("\n👤 Détails de l'utilisateur:")
        print(f"🔹 ID : {user.id}")
        print(f"🔹 Nom : {user.name}")
        print(f"🔹 Email : {user.email}")
        print(f"🔹 Rôle : {role_name}")
        if user.clients:
            print(f"🔹 Clients gérés : {[client.name for client in user.clients]}")
        if user.events:
            print(f"🔹 Événements suivis : {[event.title for event in user.events]}")

    def display_info_message(self, message):
        """Affiche un message d'information."""
        print(f"ℹ️ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")
