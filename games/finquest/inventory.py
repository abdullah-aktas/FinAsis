# -*- coding: utf-8 -*-
"""
FinQuest 3D - Inventory helpers
"""
from __future__ import annotations
from typing import Any


def has_diverse_inventory(game: Any, min_categories: int = 3) -> bool:
    categories = set()
    inventory = game.game_state.get("player", {}).get("inventory", {})
    market_products = game.game_state.get("market", {}).get("products", {})
    for product_name in inventory.keys():
        if product_name in market_products:
            categories.add(market_products[product_name].get("category"))
    return len(categories) >= min_categories
