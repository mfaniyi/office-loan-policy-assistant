from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from office_loan_policy_assistant.db.database import Base


# Define the user authentication table
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255),nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False,)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"),unique=True,nullable=False)
    employee = relationship("Employee")