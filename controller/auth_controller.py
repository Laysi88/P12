import jwt
from datetime import datetime, timedelta, timezone
from utils.config import SECRET_KEY, Session
from model.user import User
from view.auth_view import AuthView


class AuthController:
    def __init__(self):
        self.view = AuthView()
        self.session = Session()

    def generate_token(self, user):
        """Génère un token JWT pour un utilisateur."""
        payload = {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "role": user.role.name if user.role else None,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def decode_token(self, token):
        """Vérifie et décode un token JWT."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Token expiré. Veuillez vous reconnecter.")
            return None
        except jwt.InvalidTokenError:
            print("❌ Token invalide.")
            return None

    def store_token(self, token):
        """Stocke le token localement (fichier .token)."""
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        with open(".token", "w") as file:
            file.write(token)

    def load_token(self):
        """Charge le token stocké localement."""
        try:
            with open(".token", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    def login(self):
        """Authentifie un utilisateur et génère un token JWT."""
        email, password = self.view.prompt_credentials()
        user = self.session.query(User).filter_by(email=email).first()

        if user and user.check_password(password):
            token = self.generate_token(user)
            self.store_token(token)
            self.view.display_success_message(f"✅ Connexion réussie ! Bienvenue {user.name}.")
            return token
        else:
            self.view.display_error_message("❌ Échec de connexion. Vérifiez vos identifiants.")
            return None

    def verify_token(self):
        """Vérifie si un token JWT valide est stocké et retourne l'utilisateur associé."""
        token = self.load_token()
        if not token:
            self.view.display_error_message("⚠️ Vous devez vous connecter !")
            return None

        payload = self.decode_token(token)
        if not payload:
            return None

        user = self.session.query(User).filter_by(id=payload["user_id"]).first()
        if not user:
            self.view.display_error_message("⚠️ Utilisateur introuvable.")
            return None

        return user

    def logout(self):
        """Déconnecte l'utilisateur en supprimant le token."""
        open(".token", "w").close()
        self.view.display_success_message("👋 Déconnexion réussie.")
