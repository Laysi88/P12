from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils.config import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    users = relationship("User", back_populates="role")

    def get_permissions(self):
        """Retourne l'ensemble des permissions pour un rôle donné."""
        role_permissions = {
            "gestion": {
                "create_user",
                "read_user",
                "update_user",
                "delete_user",
                "create_contrat",
                "update_contrat",
                "read_contrat",
                "filter_contrat",
            },
            "commercial": {
                "create_client",
                "read_client",
                "update_client",
                "create_contrat",
                "read_contrat",
                "update_contrat",
                "read_contrat",
                "filter_contrat",
            },
            "support": {},
        }
        return role_permissions.get(self.name, set())

    def has_permission(self, action: str) -> bool:
        """Vérifie si le rôle a une permission spécifique."""
        return action in self.get_permissions()
