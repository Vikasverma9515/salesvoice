import { useEffect, useRef } from "react";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatViewProps {
    messages: Message[];
}

export function ChatView({ messages }: ChatViewProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="flex flex-col space-y-4 p-4 overflow-y-auto h-full">
            {messages.length === 0 && (
                <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm">
                    Start speaking to place an order...
                </div>
            )}

            {messages.map((msg, index) => (
                <div
                    key={index}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                        }`}
                >
                    <div
                        className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === "user"
                            ? "bg-white text-black rounded-br-sm"
                            : "bg-zinc-900 text-white rounded-bl-sm border border-zinc-800"
                            }`}
                    >
                        {msg.content}
                    </div>
                </div>
            ))}
            <div ref={messagesEndRef} />
        </div>
    );
}
