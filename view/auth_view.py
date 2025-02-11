class AuthView:
    def prompt_credentials(self):
        """Demande à l'utilisateur de saisir ses identifiants."""
        email = input("📧 Email : ")
        password = input("🔑 Mot de passe : ")
        return email, password

    def display_success_message(self, message):
        """Affiche un message de succès."""
        print(f"✅ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")
