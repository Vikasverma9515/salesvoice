import json
import os
from typing import List, Dict, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/products.json")


def load_products() -> List[Dict]:
    """Loads products from the JSON file."""
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def get_products(
    query: Optional[str] = None, max_price: Optional[float] = None
) -> List[Dict]:
    """
    Search products by name/category and/or max price (used by tool calling).
    """
    products = load_products()
    results = []

    print(f"DEBUG: get_products called with query={query}, max_price={max_price}")

    if max_price is not None:
        try:
            max_price = float(max_price)
        except ValueError:
            print(f"ERROR: Could not cast max_price {max_price} to float")
            max_price = None

    for p in products:
        # Filter by name or category (case-insensitive) if query is provided
        if query:
            q_lower = query.lower()
            if (
                q_lower not in p["name"].lower()
                and q_lower not in p["category"].lower()
            ):
                continue

        # Filter by price
        if max_price is not None and p["price"] > max_price:
            continue

        results.append(p)

    return results


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Get a single product by ID."""
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def update_product_stock(product_id: str, quantity_sold: int) -> bool:
    """Updates the stock of a product."""
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            if p["stock"] >= quantity_sold:
                p["stock"] -= quantity_sold
                with open(DATA_PATH, "w") as f:
                    json.dump(products, f, indent=2)
                return True
            return False
    return False
