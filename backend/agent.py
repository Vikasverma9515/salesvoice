import json
import logging
import os
from typing import Annotated

from dotenv import load_dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import deepgram, openai, silero

from tools import (
    search_products as db_search_products,
    create_order as db_create_order,
)

load_dotenv()
logger = logging.getLogger("salesvoice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["first_user_interaction"] = True


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the user to join
    participant = await ctx.wait_for_participant()
    logger.info(f"participant joined: {participant.identity}")

    @llm.function_tool
    async def search_products(
        query: Annotated[
            str,
            "The name or category of product to search for (e.g., 'Coca Cola', 'Drinks').",
        ],
        max_price: Annotated[int, "The maximum price of the product. Optional."] = 0,
    ):
        """Search for products in the catalog based on name, category or price."""
        print(
            f"DEBUG: agent.search_products wrapper called with query={query}, max_price={max_price}"
        )
        # Handle the '0' default or None if passed explicitly
        if max_price and max_price > 0:
            try:
                max_price_float = float(max_price)
            except ValueError:
                print(f"ERROR: agent wrapper could not cast max_price {max_price}")
                max_price_float = None
        else:
            max_price_float = None

        return db_search_products(query, max_price_float)

    @llm.function_tool
    async def confirm_order(
        confirmed: Annotated[bool, "Whether to confirm the order."] = True,
    ):
        """Confirm the order and finalize the purchase."""
        print("DEBUG: confirm_order called")
        payload = json.dumps({"type": "ORDER_FINALIZED"})
        await ctx.room.local_participant.publish_data(payload, reliable=True)
        return "Order confirmed and finalized successfully."

    @llm.function_tool
    async def create_order(
        product_id: Annotated[str, "The ID of the product to order."],
        quantity: Annotated[int, "The quantity to order."],
    ):
        """Create an order for a product."""
        result = db_create_order(product_id, quantity)

        # Publish order event to the room ONLY if successful
        if "error" not in result and "id" in result:
            payload = json.dumps({"type": "ORDER_CONFIRMED", "data": result})
            await ctx.room.local_participant.publish_data(payload, reliable=True)

        return result

    # System prompt
    system_prompt = (
        "You are Maya, a friendly sales assistant for 'Salesvoice', a quick-commerce store. "
        "Your interface has a visual product catalog and shopping cart that the user can see. "
        "Your GOAL is to help customers find products and build their cart naturally. "
        "\\n\\n"
        "**CRITICAL WORKFLOW:**\\n"
        "1. When a customer asks about products, use `search_products` to check availability\\n"
        "2. When a customer wants to buy something, use `create_order` to ADD it to their cart\\n"
        "3. After adding items, let the customer review their cart - they can see it on screen\\n"
        "4. Customers can add more items, ask questions, or modify their order\\n"
        "5. ONLY call `confirm_order` when the customer EXPLICITLY says they want to finalize/confirm/place the order\\n"
        "\\n"
        "**IMPORTANT RULES:**\\n"
        "- Do NOT call `confirm_order` immediately after adding items to cart\\n"
        "- Do NOT assume the customer is ready to checkout - let them review first\\n"
        "- After using `create_order`, say something like 'I've added that to your cart' and ask if they want anything else\\n"
        "- You must ONLY sell items actually in the catalog. If they ask for something else, apologize and suggest alternatives\\n"
        "- If `create_order` fails due to stock, explain the situation and offer the available quantity\\n"
        "- Be concise, friendly, and natural in your responses\\n"
        "- Suggest upsells when appropriate (e.g., chips with drinks)\\n"
        "- Currencies are in INR (₹)\\n"
    )

    # Create the agent definition
    agent = Agent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY")),
        llm=openai.LLM(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
        ),
        tts=deepgram.TTS(api_key=os.getenv("DEEPGRAM_API_KEY")),
        tools=[search_products, create_order, confirm_order],
        instructions=system_prompt,
    )

    # Create and start the session
    session = AgentSession()
    # Adding to chat context for history if needed, but agent handles instructions internally now.

    await session.start(agent, room=ctx.room)

    # Initial Greeting
    await session.say(
        "Hey! I'm Maya, your sales assistant. What can I get for you today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
