from .units import to_kg

RATE_PER_KG = {"standard": 4.0, "express": 9.0}


def shipping_cost(weight_g, service):
    return round(to_kg(weight_g) * RATE_PER_KG[service], 2)
