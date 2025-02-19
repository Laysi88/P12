from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import datetime
from utils.config import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(100))
    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    commercial_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    commercial = relationship("User", back_populates="clients")
    contrats = relationship("Contrat", back_populates="client", passive_deletes="all")

    def __init__(self, name, email, phone=None, company=None, commercial_id=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.company = company
        self.commercial_id = commercial_id
        self.date_created = datetime.datetime.now()
        self.date_updated = datetime.datetime.now()

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, email={self.email}, company={self.company}, commercial_id={self.commercial_id})>"
