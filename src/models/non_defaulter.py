from sqlalchemy import Column, Integer, String, Numeric
from database import Base

class NonDefaulter(Base):
    __tablename__ = 'non_defaulters'
    
    nrow = Column(Integer, primary_key=True)
    userId = Column(String(150), nullable=False, unique=True)
    demographics = Column(Numeric(10, 6))
    financialResponsibility = Column(Numeric(10, 6))
    riskAversion = Column(Numeric(10, 6))
    impulsivity = Column(Numeric(10, 6))
    futureOrientation = Column(Numeric(10, 6))
    financialKnowledge = Column(Numeric(10, 6))
    locusOfControl = Column(Numeric(10, 6))
    socialInfluence = Column(Numeric(10, 6))
    resilience = Column(Numeric(10, 6))
    familismo = Column(Numeric(10, 6))
    respect = Column(Numeric(10, 6))
    risk_level = Column(Numeric(10, 6))

    def to_dict(self):
        return {
            'userId': self.userId,
            'demographics': float(self.demographics) if self.demographics else None,
            'financialResponsibility': float(self.financialResponsibility) if self.financialResponsibility else None,
            'riskAversion': float(self.riskAversion) if self.riskAversion else None,
            'impulsivity': float(self.impulsivity) if self.impulsivity else None,
            'futureOrientation': float(self.futureOrientation) if self.futureOrientation else None,
            'financialKnowledge': float(self.financialKnowledge) if self.financialKnowledge else None,
            'locusOfControl': float(self.locusOfControl) if self.locusOfControl else None,
            'socialInfluence': float(self.socialInfluence) if self.socialInfluence else None,
            'resilience': float(self.resilience) if self.resilience else None,
            'familismo': float(self.familismo) if self.familismo else None,
            'respect': float(self.respect) if self.respect else None,
            'riskLevel': float(self.risk_level) if self.risk_level else None,
        }