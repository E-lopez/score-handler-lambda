from __future__ import annotations
from abc import ABC, abstractmethod
import locale
from typing import List
from models.defaults.defaults_dict import document_defaults
from utils.functions import get_default
import re

loc = locale.getlocale()
locale.setlocale(locale.LC_MONETARY, loc)

class QuestionScoring():
  def __init__(self, strategy = None) -> None:
    self._strategy = self.select_scoring(strategy)

  def select_scoring(self, strategy):
    if strategy == 'demographics':
      return DemographicsScoring()
    else:
      return Default()

  def set_scoring(self, strategy: Strategy):
    self._strategy = strategy

  def use_scoring(self, *args):
    return self._strategy.score_question(*args)


class Strategy(ABC):
  @abstractmethod
  def score_question(self, *args: List):
    pass


class Default(Strategy):
  def __init__(self):
        self.count = 0
        self.data = {}

  def score_question(self, *args, i = 0):
    if(len(self.data) == 0):
      self.data = {**self.data, **(dict(args[0]['data']))}
    if(i == len(self.data)):
      return self.count/len(self.data)
    key = list(self.data)[i]
    print(f"Scoring field: {key} with value: {self.data[key]}")
    value = int(self.data[key])
    partial = value if isinstance(value, int) else 3
    self.count = self.count + partial
    print(f"Current count: {self.count}, Partial score: {partial}. Len: {len(self.data)}, Value type: {isinstance(value, int)}")
    return self.score_question(self, args, i = i+1)


class DemographicsScoring(Strategy):
  def __init__(self):
        self.count = 0
        self.data = {}

  def field_score(self, key) -> float:
    data = self.data[key]
    print(f"Scoring field: {key} with value: {data}. Data is F: {data == 'F'}, data is Desempleado: {data == 'Desempleado'}")
    if key == 'gender':
      return 5.0 if data == 'F' else 0
    elif key == 'occupation':
      return 0 if data == 'Desempleado' else 5.0
    else:
      return 0.0

  def score_question(self, *args, i = 0):
    if(len(self.data) == 0):
      self.data = {**self.data, **(dict(args[0]))}
    if(i == len(self.data)):
      return self.count
    key = list(self.data)[i]
    self.count = self.count + self.field_score(key)
    return self.score_question(self, args, i = i+1)
       