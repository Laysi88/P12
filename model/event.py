from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, validates
from utils.config import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contrat_id = Column(Integer, ForeignKey("contrats.id", ondelete="SET NULL"), nullable=False)
    contrat = relationship("Contrat", back_populates="event")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    support_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    support = relationship("User", back_populates="events")
    location = Column(String(100), nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String(255))

    def __init__(self, name, contrat_id, start_date, end_date, location, attendees, support_id=None, notes=None):
        """Initialisation d'un événement."""
        self.name = name
        self.contrat_id = contrat_id
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.attendees = attendees
        self.support_id = support_id
        self.notes = notes

    @validates("start_date", "end_date")
    def validate_dates(self, key, value):
        """Vérifie que la date de début précède bien la date de fin."""
        if key == "end_date" and value < self.start_date:
            raise ValueError("La date de fin doit être postérieure à la date de début.")
        return value

    @validates("attendees")
    def validate_attendees(self, key, value):
        """Empêche un nombre négatif de participants."""
        if value < 0:
            raise ValueError("Le nombre de participants ne peut pas être négatif.")
        return value

    def __repr__(self):
        return (
            f"<Event(id={self.id}, name={self.name}, start_date={self.start_date}, "
            f"end_date={self.end_date}, location={self.location}, attendees={self.attendees})>"
        )
