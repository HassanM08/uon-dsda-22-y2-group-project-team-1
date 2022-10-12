import pydantic import Base

class PersonInfo(Base):
    name: str
    age: int
    height: float
