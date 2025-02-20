from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from utils.config import Base


class Contrat(Base):
    __tablename__ = "contrats"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship("Client", back_populates="contrats")
    event = relationship("Event", back_populates="contrat", uselist=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    status = Column(Boolean, default=False)

    def __init__(self, client_id, total_amount, remaining_amount, status=False):
        """Initialisation d'un contrat."""
        self.client_id = client_id
        self.total_amount = total_amount
        self.remaining_amount = remaining_amount
        self.status = status

    def sign_contrat(self):
        """Marque le contrat comme signé."""
        self.status = True

    def __repr__(self):
        return (
            f"<Contrat(id={self.id}, client_id={self.client_id}, total_amount={float(self.total_amount)}, "
            f"remaining_amount={float(self.remaining_amount)}, "
            f"date_created={self.date_created if self.date_created else 'None'}, status={self.status})>"
        )

    @validates("remaining_amount", "total_amount")
    def validate_amounts(self, key, value):
        """Empêche les montants négatifs et le montant restant supérieur au total."""
        if value < 0:
            raise ValueError(f"{key} ne peut pas être négatif.")
        if key == "remaining_amount" and value > self.total_amount:
            raise ValueError("Le montant restant ne peut pas dépasser le montant total.")
        return value
