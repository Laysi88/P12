from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from utils.config import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(100))
    date_created = Column(DateTime)
    date_updated = Column(DateTime)
    commercial_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    commercial = relationship("User", back_populates="clients")
    contrats = relationship("Contrat", back_populates="client", passive_deletes="all")
