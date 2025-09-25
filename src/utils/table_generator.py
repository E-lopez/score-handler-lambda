from __future__ import annotations
from abc import ABC, abstractmethod
from math import ceil
from operator import itemgetter
from typing import List
import logging
from datetime import date
# Removed numpy_financial to avoid numpy dependency
# Using basic financial formulas instead
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from utils.functions import cast_value, map_risk_to_rate

logger = logging.getLogger(__name__)   


class TableGenerator():
  def __init__(self, strategy = None) -> None:
    self._strategy = self.select_method(strategy)

  def select_method(self, strategy):
    if strategy == 'repayment_plan_period':
      return GenerateByPeriod()
    elif strategy == 'repayment_plan_installment':
      return GenerateByinstallment()
    else:
      return 'Not Implemented'
      
  def set_method(self, strategy: Strategy):
    self._strategy = strategy

  def use_method(self, **kwargs):
    return self._strategy.generate_table(**kwargs)


class Strategy(ABC):
  @abstractmethod
  def generate_table(self, **kwargs: List):
    pass

  def parse_args(self, **kwargs: List):
    return {
      k: (lambda k, x=v: cast_value(k, x) if x != 'null' else x)
      (k, v) for k, v in kwargs.items()
    }
  
  def calculate_values(self, r, period, amount):
    results = []
    balance = amount
    
    for i in range(1, int(period) + 1):
      # Basic financial calculations without numpy
      monthly_rate = r/12
      payment = amount * (monthly_rate * (1 + monthly_rate)**period) / ((1 + monthly_rate)**period - 1)
      
      # Calculate interest and principal for this period
      interest = balance * monthly_rate
      principal = payment - interest
      balance = balance - principal
      
      payment_date = date.today() + relativedelta(months=i-1)
      service_fee = amount * 0.015  # Assuming 1.5% service fee
      insurance_fee = amount * (r/100) # Assuming insurance fee based on risk rate
      
      results.append({
        'period': i,
        'due_date': payment_date.isoformat(),
        'installment': round(payment, 2) + service_fee + insurance_fee,
        'principal': round(principal, 2),
        'interest': round(interest, 2),
        'service_fee': service_fee,
        'insurance_fee': insurance_fee,
        'balance': round(balance, 2)
      })
    
    return results


class GenerateByPeriod(Strategy):
  def generate_table(self, **kwargs):
    user_risk, period, amount = itemgetter('user_risk', 'period', 'amount')(self.parse_args(**kwargs))
    r = map_risk_to_rate(user_risk)
    res = self.calculate_values(r=r, period=period, amount=amount)
    data = {'data': res, 'rate': r}
    return data


class GenerateByinstallment(Strategy):
  def generate_table(self, **kwargs):
    user_risk, installment, amount = itemgetter('user_risk', 'installment', 'amount')(self.parse_args(**kwargs))
    r = map_risk_to_rate(user_risk)
    # Calculate number of periods using basic formula
    monthly_rate = float(r/12)
    payment = float(installment)
    principal = float(amount)
    
    if monthly_rate == 0:
      period = principal / payment
    else:
      import math
      period = math.log(1 + (principal * monthly_rate) / payment) / math.log(1 + monthly_rate)
    
    period = round(period)
    res = self.calculate_values(r=r, period=period, amount=amount)
    data = {'data': res, 'rate': r}
    return data
