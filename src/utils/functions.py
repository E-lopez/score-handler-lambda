from math import ceil
from models.defaults.defaults_dict import document_defaults


def calculate_coords(values, key, presets):
  right_column = ['Renta2', 'Ganancias_ocasionales', 'Impuestos_renta_liquida', 'Liquidacion_privada', 'Retenciones']
  right_offset = ['Impuestos_renta_liquida', 'Retenciones']
  if key in ['informacion_general', 'pago_total', 'pie_de_pagina', 'obras_por_impuestos']:
    x0 = values[0]
    top = values[1]
    x1 = x0 + values[2]
    bottom = top + values[3]
    return (x0, top, x1, bottom)
  else:
    selected_preset = 'right' if key in right_column else 'left'
    x_offset = 15.09 if key in right_offset else 0

    x0, width, height = presets[selected_preset].values()
    x0 += x_offset
    width -= x_offset
    top = float(values)
    x1 = x0 + width
    bottom = top + height
    return (x0, top, x1, bottom)
      
     
def get_default(document, index, version):
    try:
      default = document_defaults[document][version][index]
      return default
    except KeyError:
      return 'n/a'
    

def map_risk_to_rate(value):
  if value >= 10.0 and value <= 13.0:
    return 0.24
  elif value >= 7.5 and value < 10.0:
    return 0.25
  else:
    return 0.0
    

def cast_value(key, value):
  if(key == 'user_risk'):
    return float(value)
  else:
    return int(value)
