import os
import json
from groq import Groq
from backend.tools import TOOLS_SCHEMA, search_products, create_order
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """
You are a helpful and friendly sales assistant for a quick-commerce store.
Your goal is to help users find products, answer questions about price/availability, and place orders.
You have access to a product catalog via tools.
- If a user asks for products, use `search_products`.
- If a user wants to buy something, use `create_order`.
- Be concise and natural in your responses, as they will be spoken out loud.
- Suggest upsells naturally (e.g., "Would you like some chips with that drink?").
- Currencies are in INR (₹).
"""


def chat_with_agent(messages: list) -> str:
    """
    Sends messages to Groq, handles tool calls, and returns the final response.
    """
    if not client:
        return "Error: GROQ_API_KEY not configured."

    # Add system prompt if not present
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto",
        max_tokens=1024,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        # Append the assistant's message with tool calls to history
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            tool_output = ""

            if function_name == "search_products":
                tool_output = search_products(
                    category=function_args.get("category"),
                    max_price=function_args.get("max_price"),
                )
            elif function_name == "create_order":
                tool_output = create_order(
                    product_id=function_args.get("product_id"),
                    quantity=function_args.get("quantity"),
                )

            # Append tool output to history
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output,
                }
            )

        # Get final response from LLM after tool outputs
        second_response = client.chat.completions.create(
            model="llama3-70b-8192", messages=messages
        )
        return second_response.choices[0].message.content or ""

    return response_message.content or ""
