from prompt_toolkit import prompt
from rich.console import Console
from controller.auth_controller import AuthController
from controller.user_controller import UserController
from controller.contrat_controller import ContratController
from controller.event_controller import EventController
from controller.client_controller import ClientController
from utils.config import Base, engine, Session
from utils.populate_database import seed_roles, seed_admin_user
import sys
from model import Role, User
from view.menu_view import show_menu, show_user_menu, show_client_menu, show_contrat_menu, show_event_menu
import sentry_sdk

console = Console()
auth_controller = AuthController()


def initialize_database():
    """Ajoute les rôles et l'admin s'ils n'existent pas encore."""
    Base.metadata.create_all(engine)
    session = Session()
    if session.query(Role).count() == 0:
        print("📌 Création des rôles...")
        seed_roles(session)
    admin_exists = (
        session.query(User).join(Role).filter(User.email == "admin@admin.com", Role.name == "gestion").first()
    )

    if admin_exists is None:
        print("📌 Création de l'admin par défaut...")
        seed_admin_user(session)

    session.close()


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "login":
            auth_controller.login()
            return
        elif sys.argv[1] == "logout":
            auth_controller.logout()
            console.print("\n[bold yellow]🚪 Déconnexion réussie ![/bold yellow]")
            return

    user = auth_controller.verify_token()
    if not user:
        console.print("\n🔐 Connectez-vous d'abord avec `python menu.py login`")
        return

    controllers = {
        "user": UserController(user),
        "client": ClientController(user),
        "contrat": ContratController(user),
        "event": EventController(user),
    }

    while True:
        show_menu(user)
        choix = prompt("👉 Choisissez une option : ").strip().lower()

        if choix == "1":
            show_user_menu(user, controllers)

        elif choix == "2":
            show_client_menu(user, controllers)

        elif choix == "3":
            show_contrat_menu(user, controllers)

        elif choix == "4":
            show_event_menu(user, controllers)

        elif choix == "0":
            console.print("[bold red]👋 Au revoir ![/bold red]")
            break

        elif choix == "l":
            auth_controller.logout()
            console.print("\n[bold yellow]🚪 Déconnexion réussie ![/bold yellow]")
            break

        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


if __name__ == "__main__":
    try:
        sentry_sdk.set_context("CLI Command", {"command": " ".join(sys.argv) if sys.argv else "Menu principal"})

        initialize_database()
        main()
    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        sentry_sdk.capture_exception(e)
        console.print(f"[bold red]🚨 Une erreur s'est produite : {e}[/bold red]")
