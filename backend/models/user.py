from sqlalchemy import Integer,Column,String,DateTime
from sqlalchemy.sql import func
from backend.database import Base

class User(Base):
    __tablename__= "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String(300),unique=True,nullable=False,index=True)
    hashed_password = Column(String(300),nullable=False,)
    #is_active = Column(Boolean,nullable=False,default=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)