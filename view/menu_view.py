from rich.console import Console
from prompt_toolkit import prompt

console = Console()


def show_menu(user):
    """Affiche le menu principal en fonction du rôle de l'utilisateur."""
    console.print(f"\n🔐 [bold cyan]Connecté en tant que {user.name} - {user.role.name}[/bold cyan]")
    console.print("[bold cyan]=== Menu Principal ===[/bold cyan]")

    console.print("1️⃣ [green]Gérer les utilisateurs[/green]")
    console.print("2️⃣ [purple]Gérer les clients[/purple]")
    console.print("3️⃣ [blue]Gérer les contrats[/blue]")
    console.print("4️⃣ [magenta]Gérer les événements[/magenta]")

    console.print("0️⃣ [red]Quitter[/red]")
    console.print("🔑 [yellow]Logout (L)[/yellow]")


def show_user_menu(user, controllers):
    """Affiche le menu pour la gestion des utilisateurs."""
    console.print("[bold green]=== Gestion des utilisateurs ===[/bold green]")

    if user.role.name == "gestion":
        console.print("1️⃣ [blue]Créer un utilisateur[/blue]")
    console.print("2️⃣ [cyan]Lister les utilisateurs[/cyan]")
    console.print("3️⃣ [magenta]Information sur un utilisateur[/magenta]")
    if user.role.name == "gestion":
        console.print("4️⃣ [magenta]Modifier un utilisateur[/magenta]")
        console.print("5️⃣ [red]Supprimer un utilisateur[/red]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1" and user.role.name == "gestion":
            controllers["user"].create_user()

        elif sub_choix == "2":
            controllers["user"].list_users()
        elif sub_choix == "3":
            try:
                user_id = int(prompt("👉 Entrez l'ID de l'utilisateur : ").strip())
                controllers["user"].get_user_details(user_id)
            except ValueError:
                console.print("[bold yellow]⚠ ID invalide, veuillez entrer un nombre.[/bold yellow]")

        elif sub_choix in ["4", "5"] and user.role.name == "gestion":
            action = "modifier" if sub_choix == "4" else "supprimer"

            try:
                user_id = int(prompt(f"👉 Entrez l'ID de l'utilisateur à {action} : ").strip())
                if sub_choix == "4":
                    controllers["user"].update_user(user_id)
                else:
                    controllers["user"].delete_user(user_id)
            except ValueError:
                console.print("[bold yellow]⚠ ID invalide, veuillez entrer un nombre.[/bold yellow]")

        elif sub_choix == "0":
            break

        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


def show_client_menu(user, controllers):
    """Affiche le menu pour la gestion des clients."""

    console.print("[bold purple]=== Gestion des clients ===[/bold purple]")
    if user.role.name == "commercial":
        console.print("1️⃣ [blue]Créer un client[/blue]")
        console.print("2️⃣ [cyan]Lister mes clients[/cyan]")
        console.print("3️⃣ [magenta]Modifier un client[/magenta]")
    console.print("4️⃣ [magenta]Lister tous les clients[/magenta]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1" and user.role.name == "commercial":
            controllers["client"].create_client()
        elif sub_choix == "2" and user.role.name == "commercial":
            controllers["client"].list_personnal_client()
        elif sub_choix == "3" and user.role.name == "commercial":
            try:
                client_id = int(prompt("👉 Entrez l'ID du client à modifier : ").strip())
                controllers["client"].update_client(client_id)
            except ValueError:
                console.print("[bold yellow]⚠ ID invalide! Non existant ou ne vous est pas attribué[/bold yellow]")
        elif sub_choix == "4":
            controllers["client"].list_all_client()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


def show_contrat_menu(user, controllers):
    """Affiche le menu pour la gestion des contrats."""
    console.print("[bold blue]=== Gestion des contrats ===[/bold blue]")
    if user.role.name == "commercial":
        console.print("1️⃣ [blue]Créer un contrat[/blue]")
    console.print("2️⃣ [cyan]Lister les contrats[/cyan]")
    if user.role.name == "commercial" or user.role.name == "gestion":
        console.print("3️⃣ [magenta]Modifier un contrat[/magenta]")
        console.print("4️⃣ [magenta]Filtrer les contrats[/magenta]")
    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1" and user.role.name == "commercial":
            controllers["contrat"].create_contrat()
        elif sub_choix == "2":
            controllers["contrat"].read_contrat()
        elif sub_choix == "3" and user.role.name in ["commercial", "gestion"]:
            contrat_id = int(prompt("👉 Entrez l'ID du contrat à modifier : ").strip())
            try:
                controllers["contrat"].update_contrat(contrat_id)
            except ValueError as ve:
                console.print(f"[bold red]🚨 Erreur : {ve}[/bold red]")

        elif sub_choix == "4" and user.role.name == "commercial" or user.role.name == "gestion":
            controllers["contrat"].filter_contrats()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")


def show_event_menu(user, controllers):
    """Affiche le menu pour la gestion des événements."""
    console.print("[bold magenta]=== Gestion des événements ===[/bold magenta]")
    if user.role.name == "commercial":
        console.print("1️⃣ [blue]Créer un événement[/blue]")

    console.print("2️⃣ [cyan]Lister les événements[/cyan]")
    if user.role.name == "support" or user.role.name == "gestion":
        console.print("3️⃣ [magenta]Mettre à jour un événement[/magenta]")
        console.print("4️⃣ [magenta]Filtrer les événements[/magenta]")

    console.print("0️⃣ [yellow]Retour au menu principal[/yellow]")

    while True:
        sub_choix = prompt("👉 Choisissez une action : ").strip()

        if sub_choix == "1" and user.role.name == "commercial":
            controllers["event"].create_event()
        elif sub_choix == "2":
            controllers["event"].read_event()
        elif sub_choix == "3" and user.role.name in ["support", "gestion"]:
            controllers["event"].update_event()
        elif sub_choix == "4" and user.role.name in ["support", "gestion"]:
            controllers["event"].filter_event()
        elif sub_choix == "0":
            break
        else:
            console.print("[bold yellow]⚠ Option invalide, essayez encore ![/bold yellow]")
