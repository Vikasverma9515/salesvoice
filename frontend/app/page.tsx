"use client";

import { LiveKitRoom, useVoiceAssistant, BarVisualizer, RoomAudioRenderer, ControlBar, useRoomContext } from "@livekit/components-react";
import "@livekit/components-styles";
import { useEffect, useState } from "react";
// import { ChatView } from "../components/ChatView";
import { ChatView } from "../components/ChatView";
import { BsStars } from "react-icons/bs";
import { motion, AnimatePresence } from "framer-motion";
import { RoomEvent, ChatMessage, Participant, TranscriptionSegment } from "livekit-client";

export default function Home() {
    const [token, setToken] = useState("");
    const [url, setUrl] = useState("");
    const [isAudioStarted, setIsAudioStarted] = useState(false);

    useEffect(() => {
        (async () => {
            try {
                const resp = await fetch("http://localhost:8000/token");
                const data = await resp.json();
                setToken(data.token);
                setUrl(data.livekit_url);
            } catch (e) {
                console.error(e);
            }
        })();
    }, []);

    if (!token) {
        return (
            <div className="flex items-center justify-center h-screen bg-slate-950 text-white">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <p className="font-outfit animate-pulse">Connecting to Salesvoice...</p>
                </div>
            </div>
        );
    }

    if (!isAudioStarted) {
        return (
            <div className="flex items-center justify-center h-screen bg-slate-950 text-white">
                <button
                    onClick={() => setIsAudioStarted(true)}
                    className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-lg shadow-lg shadow-blue-500/20 transition-all transform hover:scale-105"
                >
                    Start Experience
                </button>
            </div>
        )
    }

    return (
        <LiveKitRoom
            video={false}
            audio={true}
            token={token}
            serverUrl={url}
            className="h-screen flex flex-col bg-slate-950 overflow-hidden"
            data-lk-theme="default"
        >
            <RoomAudioRenderer />
            <MainInterface />
        </LiveKitRoom>
    );
}

interface Product {
    id: string;
    name: string;
    category: string;
    price: number;
    stock: number;
}

interface CartItem extends Product {
    quantity: number;
}

function MainInterface() {
    const { state, audioTrack } = useVoiceAssistant();
    const [messages, setMessages] = useState<any[]>([]);
    const [products, setProducts] = useState<Product[]>([]);
    const [cart, setCart] = useState<CartItem[]>([]);
    const [showSuccess, setShowSuccess] = useState(false);
    const room = useRoomContext();

    useEffect(() => {
        (async () => {
            try {
                const res = await fetch("http://localhost:8000/products");
                const data = await res.json();
                setProducts(data);
            } catch (e) {
                console.error("Failed to fetch products", e);
            }
        })();
    }, []);

    useEffect(() => {
        if (showSuccess) {
            const timer = setTimeout(() => setShowSuccess(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [showSuccess]);

    useEffect(() => {
        if (!room) return;

        const onChatMessage = (msg: ChatMessage, participant?: Participant) => {
            setMessages((prev) => [...prev, { role: participant?.isAgent ? "assistant" : "user", content: msg.message }]);
        };

        const onTranscriptionReceived = (segments: TranscriptionSegment[], participant?: Participant) => {
            const segment = segments[0];
            if (!segment || !segment.final) return;
            setMessages((prev) => [...prev, { role: participant?.isAgent ? "assistant" : "user", content: segment.text }]);
        };

        const onDataReceived = (payload: Uint8Array) => {
            try {
                const str = new TextDecoder().decode(payload);
                const event = JSON.parse(str);

                if (event.type === "ORDER_CONFIRMED") {
                    const orderData = event.data;
                    const product = products.find(p => p.id === orderData.product_id);
                    if (product) {
                        setCart(prev => {
                            const existing = prev.find(item => item.id === product.id);
                            if (existing) {
                                return prev.map(item => item.id === product.id ? { ...item, quantity: item.quantity + orderData.quantity } : item);
                            } else {
                                return [...prev, { ...product, quantity: orderData.quantity }];
                            }
                        });
                    }
                } else if (event.type === "ORDER_FINALIZED") {
                    setCart([]);
                    setShowSuccess(true);
                }
            } catch (e) {
                console.error("Failed to parse data received", e);
            }
        }

        room.on(RoomEvent.ChatMessage, onChatMessage);
        room.on(RoomEvent.TranscriptionReceived, onTranscriptionReceived);
        room.on(RoomEvent.DataReceived, onDataReceived);

        return () => {
            room.off(RoomEvent.ChatMessage, onChatMessage);
            room.off(RoomEvent.TranscriptionReceived, onTranscriptionReceived);
            room.off(RoomEvent.DataReceived, onDataReceived);
        };
    }, [room, products]);

    const totalAmount = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    return (
        <main className="flex flex-col h-screen font-sans relative bg-black text-white overflow-hidden">


            <AnimatePresence>
                {showSuccess && (
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="absolute inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md">
                        <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-2xl shadow-2xl flex flex-col items-center gap-4 max-w-sm mx-4">
                            <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
                                <BsStars className="w-8 h-8 text-white" />
                            </div>
                            <h2 className="text-2xl font-bold text-white text-center font-serif">Order Confirmed!</h2>
                            <p className="text-zinc-400 text-center text-sm">Your order has been placed successfully.</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-black h-16 shrink-0">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
                            <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2a1 1 0 0 1 2 0v2a5 5 0 0 0 10 0v-2a1 1 0 0 1 2 0z" />
                                <path d="M13 19.93V22h-2v-2.07A7.978 7.978 0 0 1 12 20c.34 0 .68-.02 1.01-.07z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold tracking-tight text-white font-serif">Salesvoice</h1>
                            <p className="text-[9px] text-zinc-500 font-medium tracking-wider uppercase">AI Voice Agent</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 text-xs text-zinc-400 font-medium border border-zinc-800">
                    <div className={`w-2 h-2 rounded-full ${state === "listening" ? "bg-white animate-pulse" : "bg-zinc-600"}`} />
                    {state}
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden relative z-0">
                <div className="w-80 border-r border-zinc-800 bg-zinc-950 flex flex-col">
                    <div className="flex flex-col h-1/3 border-b border-zinc-800 min-h-[150px]">
                        <div className="p-3 border-b border-zinc-800 bg-zinc-900 flex justify-between items-center">
                            <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Your Cart</h2>
                            <span className="text-xs font-bold text-white">₹{totalAmount}</span>
                        </div>
                        <div className="flex-1 overflow-y-auto p-3 space-y-2">
                            {cart.length === 0 ? (
                                <div className="h-full flex items-center justify-center text-xs text-zinc-600 italic">Your cart is empty</div>
                            ) : (
                                cart.map(item => (
                                    <div key={item.id} className="flex justify-between items-center p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-xs hover:border-zinc-700 transition-colors">
                                        <div className="flex flex-col gap-0.5">
                                            <span className="text-white font-semibold">{item.name}</span>
                                            <span className="text-zinc-500 text-[10px]">₹{item.price} × {item.quantity}</span>
                                        </div>
                                        <span className="font-bold text-white">₹{item.price * item.quantity}</span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    <div className="flex-1 flex flex-col overflow-hidden">
                        <div className="p-3 border-b border-zinc-800 bg-zinc-900">
                            <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Catalog</h2>
                        </div>
                        <div className="flex-1 overflow-y-auto p-3">
                            <div className="grid grid-cols-1 gap-2.5">
                                {products.map((product) => {
                                    // Get emoji icon based on product name/category
                                    const getProductIcon = (name: string, category: string) => {
                                        if (name.toLowerCase().includes('coca')) return '🥤';
                                        if (name.toLowerCase().includes('pepsi')) return '🥤';
                                        if (name.toLowerCase().includes('dew')) return '🥤';
                                        if (name.toLowerCase().includes('lays')) return '🍟';
                                        if (name.toLowerCase().includes('kurkure')) return '🍿';
                                        if (name.toLowerCase().includes('dairy') || name.toLowerCase().includes('silk')) return '🍫';
                                        if (name.toLowerCase().includes('kitkat')) return '🍫';
                                        if (category === 'Drinks') return '🥤';
                                        if (category === 'Snacks') return '🍿';
                                        if (category === 'Chocolates') return '🍫';
                                        return '🛒';
                                    };

                                    return (
                                        <div key={product.id} className="p-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 transition-all border border-zinc-800 hover:border-zinc-700 hover:shadow-lg hover:shadow-black/20 group">
                                            <div className="flex items-center gap-3">
                                                {/* Product Icon */}
                                                <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-xl shrink-0 group-hover:scale-110 transition-transform">
                                                    {getProductIcon(product.name, product.category)}
                                                </div>

                                                {/* Product Info */}
                                                <div className="flex-1 min-w-0">
                                                    <h3 className="text-sm font-semibold text-white truncate">{product.name}</h3>
                                                    <div className="flex items-center gap-2 mt-0.5">
                                                        <p className="text-[10px] text-zinc-500">{product.category}</p>
                                                        <span className="text-zinc-700">•</span>
                                                        <p className="text-[10px] text-zinc-600">Stock: {product.stock}</p>
                                                    </div>
                                                </div>

                                                {/* Price */}
                                                <div className="text-right shrink-0">
                                                    <span className="block font-bold text-white text-base">₹{product.price}</span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex-1 flex flex-col min-h-0">
                    <div className="flex-1 overflow-hidden relative min-h-0">
                        <ChatView messages={messages} />
                    </div>

                    <div className="h-20 flex items-center justify-center shrink-0">
                        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} className="flex gap-1 h-10 w-40 items-center justify-center accent-white" options={{ minHeight: 6, maxHeight: 32 }} />
                    </div>
                </div>
            </div>

            <div className="relative z-10 px-4 py-3 flex items-center justify-center gap-4 bg-black border-t border-zinc-800 h-14 shrink-0">
                <ControlBar controls={{ microphone: true, camera: false, screenShare: false, chat: false }} />
                <p className="text-zinc-500 text-[10px] font-medium">
                    <span className={state === "listening" ? "text-white" : "text-zinc-600"}>{state}</span>
                </p>
            </div>
        </main>
    );
}
