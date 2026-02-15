import os
from typing import Optional
from db import get_products, get_product_by_id, update_product_stock

# Tool Definitions for Groq/Llama 3
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in the catalog based on category or price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The name or category of product to search for (e.g., 'Coca Cola', 'Drinks').",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "The maximum price of the product.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create an order for a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The ID of the product to order.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The quantity to order.",
                    },
                },
                "required": ["product_id", "quantity"],
            },
        },
    },
]


def search_products(
    query: Optional[str] = None, max_price: Optional[float] = None
) -> str:
    """Tool implementation: Search products."""
    results = get_products(query, max_price)
    if not results:
        return "No products found matching the criteria."

    # Format as a concise string for the LLM
    response = "Found the following products:\n"
    for p in results:
        response += f"- {p['name']} (Category: {p['category']}, Price: ₹{p['price']}, ID: {p['id']})\n"
    return response


def create_order(product_id: str, quantity: int) -> dict:
    """Tool implementation: Create order."""
    print(
        f"DEBUG: create_order called with product_id={product_id}, quantity={quantity} (type: {type(quantity)})"
    )

    try:
        quantity = int(quantity)
    except ValueError:
        return {"error": f"Invalid quantity: {quantity}"}

    product = get_product_by_id(product_id)
    if not product:
        return {"error": f"Product with ID {product_id} not found."}

    # Check and update stock
    if quantity > product["stock"]:
        return {
            "error": f"Insufficient stock. Only {product['stock']} units of {product['name']} are available.",
            "available_stock": product["stock"],
        }

    # Deduct stock
    if not update_product_stock(product_id, quantity):
        return {"error": "Failed to update stock. Please try again."}

    # In a real app, this would write to a DB
    total_price = product["price"] * quantity
    return {
        "id": f"order-{os.urandom(4).hex()}",
        "product_id": product_id,
        "name": product["name"],
        "quantity": quantity,
        "price_per_unit": product["price"],
        "total_price": total_price,
        "status": "confirmed",
    }
