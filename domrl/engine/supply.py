import random
from .card import *


class SupplyPile(object):
    def __init__(self, card, qty, buyable=True):
        self.card = card
        self.qty = qty
        self.buyable = buyable

    def __str__(self):
        return str(self.card)


def choose_supply_from_kingdoms(kingdoms):
    total_piles = {}
    for kingdom_piles in kingdoms:
        total_piles.update(kingdom_piles)

    keys = total_piles.keys()

    supply_keys = random.sample(keys, 10)

    supply_piles = {
        "Curse": SupplyPile(Curse, 10),
        "Estate": SupplyPile(Estate, 8),
        "Duchy": SupplyPile(Duchy, 8),
        "Province": SupplyPile(Province, 8),
        "Copper": SupplyPile(Copper, 46),
        "Silver": SupplyPile(Silver, 40),
        "Gold": SupplyPile(Gold, 30),
    }

    for key in supply_keys:
        supply_piles[key] = total_piles[key]

    return supply_piles
