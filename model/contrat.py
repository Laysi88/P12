from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship

from utils.config import Base


class Contrat(Base):
    __tablename__ = "contrats"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship("Client", back_populates="contrats")
    event = relationship("Event", back_populates="contrat", uselist=False)
    total_amount = Column(Float)
    remaining_amount = Column(Float)
    date_created = Column(DateTime)
    status = Column(Boolean)
