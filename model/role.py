from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils.config import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    users = relationship("User", back_populates="role")
