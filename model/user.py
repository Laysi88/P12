from utils.config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    password = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"))
    role = relationship("Role", back_populates="users")
    clients = relationship("Client", back_populates="commercial", passive_deletes="all")
    events = relationship("Event", back_populates="support", passive_deletes=True)

    def __init__(self, name, email, password, role_id):
        self.name = name
        self.email = email
        self.password = self.set_password(password)
        self.role_id = role_id

    def set_password(self, password):
        ph = PasswordHasher()
        return ph.hash(password)

    def check_password(self, password):
        ph = PasswordHasher()
        try:
            return ph.verify(self.password, password)
        except VerifyMismatchError:
            return False
