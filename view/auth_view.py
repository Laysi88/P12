from prompt_toolkit import prompt
from prompt_toolkit.styles import Style


class AuthView:
    def prompt_credentials(self):
        """Demande à l'utilisateur de saisir ses identifiants avec masquage du mot de passe."""
        email = input("📧 Email : ")
        password_style = Style.from_dict({"password": "fg:white bg:black"})
        password = prompt(
            "🔑 Mot de passe : ",
            is_password=True,
            style=password_style,
        )

        return email, password

    def display_success_message(self, message):
        """Affiche un message de succès."""
        print(f"✅ {message}")

    def display_error_message(self, message):
        """Affiche un message d'erreur."""
        print(f"❌ {message}")
