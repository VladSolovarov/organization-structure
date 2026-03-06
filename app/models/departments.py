from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = 'departments'
    __table_args__ = (
        CheckConstraint('id != parent_id', name='check_not_self_parent'),
        UniqueConstraint('name', 'parent_id', name='unique_name_in_parent')
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    children: Mapped[list['Department']] = relationship(
        'Department',
        back_populates='parent',
        uselist=True
    )

    parent: Mapped['Department | None'] = relationship(
        'Department',
        back_populates='children',
        remote_side='Department.id',
        uselist=False
    )

    employees: Mapped[list['Employee']] = relationship(
        'Employee',
        uselist=True,
        back_populates='department',
        cascade='all, delete-orphan'
    )