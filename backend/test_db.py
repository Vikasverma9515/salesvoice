import asyncio
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(__file__))

from db import get_products


async def test_tools():
    print("\nTesting search_products tool...")
    try:
        # Import the wrapper from agent, not the raw tool
        from agent import search_products

        # Mocking context if needed, but search_products doesn't use it
        result = await search_products(query="snacks", max_price=100)
        print(f"DEBUG: Tool result for query='snacks':\n{result}")

        print("\nTesting search for 'Coca Cola'...")
        result_coke = await search_products(query="Coca Cola")
        print(f"DEBUG: Coke result for query='Coca Cola':\n{result_coke}")
    except Exception as e:
        print(f"ERROR in search_products tool: {e}")


async def test_stock_update():
    print("\nTesting stock update...")
    from db import update_product_stock, get_product_by_id

    # Test with product 1 (Coca Cola, Stock 50)
    p_id = "1"
    initial_stock = get_product_by_id(p_id)["stock"]
    print(f"Initial stock for {p_id}: {initial_stock}")

    # Try to buy more than stock
    success = update_product_stock(p_id, initial_stock + 10)
    print(f"Buying {initial_stock + 10} should fail: {not success}")

    # Buy 5
    success = update_product_stock(p_id, 5)
    print(f"Buying 5 should succeed: {success}")

    new_stock = get_product_by_id(p_id)["stock"]
    print(f"New stock: {new_stock} (Expected: {initial_stock - 5})")


if __name__ == "__main__":
    print("Testing get_products...")
    try:
        products = get_products()
        print(f"DEBUG: Found {len(products)} products.")
    except Exception as e:
        print(f"ERROR in get_products: {e}")

    asyncio.run(test_tools())
    asyncio.run(test_stock_update())
