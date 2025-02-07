from utils.config import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contrat_id = Column(Integer, ForeignKey("contrats.id", ondelete="SET NULL"))
    contrat = relationship("Contrat", back_populates="event")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    support_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    support = relationship("User", back_populates="events")
    location = Column(String(100))
    attendees = Column(Integer)
    notes = Column(String(255))
