from sqlalchemy import Column, Integer, String, Numeric
from database import Base

class UserAmortizationData(Base):
    __tablename__ = 'user_amortization_data'
    
    nrow = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(150), nullable=False, unique=True)
    userRisk = Column(Numeric(12, 6))
    instalment = Column(Numeric(15, 2))
    period = Column(Numeric(12, 6))
    amount = Column(Numeric(15, 2))

    def to_dict(self):
        return {
            'userId': self.userId,
            'userRisk': float(self.userRisk) if self.userRisk else None,
            'instalment': float(self.instalment) if self.instalment else None,
            'period': float(self.period) if self.period else None,
            'amount': float(self.amount) if self.amount else None
        }