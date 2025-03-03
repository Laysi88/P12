from prompt_toolkit import prompt
from rich.console import Console
from controller.auth_controller import AuthController
from controller.user_controller import UserController
from controller.contrat_controller import ContratController
from controller.event_controller import EventController
from utils.config import Base, engine, Session
from utils.populate_database import seed_roles, seed_admin_user
import sys
from model import Role, User

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


def show_menu(user):
    """Affiche le menu principal en fonction du rôle de l'utilisateur."""
    console.print(f"\n🔐 [bold cyan]Connecté en tant que {user.name} - {user.role.name}[/bold cyan]")
    console.print("[bold cyan]=== Menu Principal ===[/bold cyan]")

    if user.role.name == "gestion":
        console.print("1️⃣ [green]Gérer les utilisateurs[/green]")

    if user.role.name in ["commercial", "gestion"]:
        console.print("2️⃣ [blue]Gérer les contrats[/blue]")

    if user.role.name in ["support", "gestion"]:
        console.print("3️⃣ [magenta]Gérer les événements[/magenta]")

    console.print("0️⃣ [red]Quitter[/red]")
    console.print("🔑 [yellow]Logout (L)[/yellow]")


def show_user_menu(user, user_controller):
    """Affiche le menu pour la gestion des utilisateurs."""
    console.print("[bold green]=== Gestion des utilisateurs ===[/bold green]")

    if user.role.name == "commercial":
        console.print("1️⃣ [blue]Créer un utilisateur[/blue]")
    console.print("2️⃣ [cyan]Lister les utilisateurs[/cyan]")
    console.print("3️⃣ [magenta]Modifier un utilisateur[/magenta]")
    console.print("4️⃣ [red]Supprimer un utilisateur[/red]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1":
            user_controller.create_user()
        elif sub_choix == "2":
            user_controller.list_users()
        elif sub_choix == "3":
            user_controller.update_user()
        elif sub_choix == "4":
            user_controller.delete_user()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


def show_contrat_menu(user, contrat_controller):
    """Affiche le menu pour la gestion des contrats."""
    console.print("[bold blue]=== Gestion des contrats ===[/bold blue]")

    console.print("1️⃣ [blue]Créer un contrat[/blue]")
    console.print("2️⃣ [cyan]Lister les contrats[/cyan]")
    console.print("3️⃣ [magenta]Modifier un contrat[/magenta]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1":
            contrat_controller.create_contrat()
        elif sub_choix == "2":
            contrat_controller.list_contrats()
        elif sub_choix == "3":
            contrat_controller.update_contrat()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


def show_event_menu(user, event_controller):
    """Affiche le menu pour la gestion des événements."""
    console.print("[bold magenta]=== Gestion des événements ===[/bold magenta]")

    console.print("1️⃣ [blue]Créer un événement[/blue]")
    console.print("2️⃣ [cyan]Lister les événements[/cyan]")
    console.print("3️⃣ [magenta]Mettre à jour un événement[/magenta]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1":
            event_controller.create_event()
        elif sub_choix == "2":
            event_controller.list_events()
        elif sub_choix == "3":
            event_controller.update_event()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


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

    user_controller = UserController(user)
    contrat_controller = ContratController(user)
    event_controller = EventController(user)

    while True:
        show_menu(user)
        choix = prompt("👉 Choisissez une option : ").strip().lower()

        if choix == "1" and user.role.name == "gestion":
            show_user_menu(user, user_controller)

        elif choix == "2" and user.role.name in ["commercial", "gestion"]:
            show_contrat_menu(user, contrat_controller)

        elif choix == "3" and user.role.name in ["support", "gestion"]:
            show_event_menu(user, event_controller)

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
    initialize_database()
    main()
