'use client';

import { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    actions?: string[];
}

type AssistantChatResponse = {
    message: string;
    actions?: string[];
    status?: string;
};

function parseApiErrorMessage(error: unknown, fallback: string) {
    if (!(error instanceof Error)) return fallback;

    const apiErrorMatch = error.message.match(/^API \d+:\s*([\s\S]+)$/);
    if (!apiErrorMatch) return error.message || fallback;

    const payload = apiErrorMatch[1]?.trim();
    if (!payload) return error.message || fallback;

    try {
        const parsed = JSON.parse(payload) as { detail?: string };
        return parsed.detail || error.message || fallback;
    } catch {
        return payload;
    }
}

export default function OptikGPT() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [modelPreference, setModelPreference] = useState<string | null>(null);
    const [guestMerchantId, setGuestMerchantId] = useState('guest_merchant');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { user } = useAuth();
    const pathname = usePathname();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const syncPreference = () => {
            const stored = window.localStorage.getItem('optik_model_mode');
            setModelPreference(stored || null);
        };

        const onStorage = (event: StorageEvent) => {
            if (event.key === 'optik_model_mode') {
                setModelPreference(event.newValue || null);
            }
        };

        syncPreference();
        window.addEventListener('focus', syncPreference);
        window.addEventListener('storage', onStorage);

        return () => {
            window.removeEventListener('focus', syncPreference);
            window.removeEventListener('storage', onStorage);
        };
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const storageKey = 'optik_guest_merchant_id';
        let storedId = window.localStorage.getItem(storageKey);

        if (!storedId) {
            const suffix =
                typeof crypto !== 'undefined' && 'randomUUID' in crypto
                    ? crypto.randomUUID().replace(/-/g, '').slice(0, 12)
                    : Math.random().toString(36).slice(2, 14);
            storedId = `guest_${suffix}`;
            window.localStorage.setItem(storageKey, storedId);
        }

        setGuestMerchantId(storedId);
    }, []);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage: Message = { role: 'user', content: inputValue };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        const merchantId = user?.id || guestMerchantId;

        try {
            const data = await api<AssistantChatResponse>('/api/v1/assistant/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: userMessage.content,
                    merchant_id: merchantId,
                    page_context: pathname,
                    assistant_mode: 'enterprise',
                    model_preference: modelPreference || 'balanced',
                    context: {
                        page_context: pathname,
                        source: 'optik_gpt_widget',
                        authenticated: Boolean(user),
                    }
                }),
            });

            const assistantMessage: Message = {
                role: 'assistant',
                content: data.message || "I'm having trouble connecting right now.",
                actions: data.actions
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: unknown) {
            const fallbackMessage = parseApiErrorMessage(error, "Sorry, I'm offline right now.");
            setMessages(prev => [...prev, { role: 'assistant', content: fallbackMessage }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="mb-4 w-[350px] h-[500px] bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-white/10 bg-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-lg flex items-center justify-center text-sm">🧠</div>
                                <div>
                                    <div className="font-bold text-white text-sm">Optik Ultimate AI</div>
                                    <div className="text-[10px] text-green-400 font-mono flex items-center gap-1">
                                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /> UNIVERSAL
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.length === 0 && (
                                <div className="text-center mt-10 opacity-50">
                                    <div className="text-4xl mb-2">🌟</div>
                                    <p className="text-sm text-gray-300 font-bold">Optik Ultimate AI</p>
                                    <p className="text-xs text-gray-400 mt-1">Claude + GPT-4 + Shopify + Market Intelligence</p>
                                    <p className="text-sm text-gray-300 mt-3">How can I help you build the future today?</p>
                                </div>
                            )}

                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none'
                                            : 'bg-white/10 text-gray-200 rounded-bl-none'
                                            }`}
                                    >
                                        {msg.content}
                                        {msg.actions && msg.actions.length > 0 && (
                                            <div className="mt-2 pt-2 border-t border-white/10 flex flex-wrap gap-2">
                                                {msg.actions.map(action => (
                                                    <span key={action} className="text-[10px] bg-white/10 px-2 py-1 rounded text-blue-300 font-mono">
                                                        {action}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-white/10 p-3 rounded-2xl rounded-bl-none flex gap-1">
                                        <motion.span
                                            className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                                            animate={{ y: [0, -5, 0] }}
                                            transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                                        />
                                        <motion.span
                                            className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                                            animate={{ y: [0, -5, 0] }}
                                            transition={{ duration: 0.6, repeat: Infinity, delay: 0.1 }}
                                        />
                                        <motion.span
                                            className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                                            animate={{ y: [0, -5, 0] }}
                                            transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                                        />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t border-white/10 bg-white/5">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                    placeholder="Ask anything..."
                                    className="flex-1 bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!inputValue.trim() || isLoading}
                                    className="bg-blue-600 text-white p-2 rounded-xl hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    ➤
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="flex justify-end">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="w-16 h-16 bg-gradient-to-tr from-blue-600 via-primary to-purple-600 rounded-full shadow-[0_0_30px_rgba(37,99,235,0.6)] flex items-center justify-center text-3xl text-white hover:scale-110 active:scale-95 transition-all border-2 border-white/20 animate-bounce-slow relative group"
                >
                    <span className="sr-only">Open Optik Ultimate AI</span>
                    {isOpen ? '✕' : '✨'}

                    {!isOpen && (
                        <div className="absolute bottom-full right-0 mb-4 w-64 bg-slate-900/90 backdrop-blur-xl border border-white/10 p-3 rounded-2xl shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none transform translate-y-2 group-hover:translate-y-0">
                            <p className="text-xs text-gray-300">
                                🚀 Ultimate AI: Claude + GPT-4 + Shopify + Market Intelligence
                            </p>
                        </div>
                    )}
                </button>
            </div>
        </div>
    );
}
