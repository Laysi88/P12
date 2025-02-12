class BaseController:
    def __init__(self, user, session):
        """Initialise le contrôleur avec l'utilisateur connecté."""
        self.user = user
        self.session = session

    def check_permission(self, action):
        """Vérifie si l'utilisateur connecté a la permission d'effectuer une action."""
        print(f"🔍 Vérification permission : action={action}, rôle={self.user.role.name if self.user.role else None}")

        if self.user.role and self.user.role.has_permission(action):
            print("✅ Permission accordée")
            return True
        else:
            print("⛔ Permission refusée")
            return False
