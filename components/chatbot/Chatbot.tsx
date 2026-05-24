"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send } from "lucide-react";
import { useLanguage } from "@/lib/language-context";
import { getAIResponse, generateId } from "@/lib/chatbot";
import { suggestedPrompts } from "@/data/chatbot";
import { ChatMessage } from "@/types";

interface ChatbotProps {
  initialQuery?: string;
}

export default function Chatbot({ initialQuery }: ChatbotProps) {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      text: "Hello! I'm AgriSense AI 🌱 — your expert farming assistant. I can help with crop diseases, fertilizers, irrigation, pest control, and smart farming practices. What would you like to know today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  // Handle initial query from URL
  useEffect(() => {
    if (initialQuery) {
      setInput(initialQuery);
      setTimeout(() => sendMessage(initialQuery), 400);
    }
  }, [initialQuery]);

  async function sendMessage(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg) return;
    setInput("");

    const userMsg: ChatMessage = { id: generateId(), text: msg, isUser: true, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setTyping(true);

    await new Promise((r) => setTimeout(r, 1000 + Math.random() * 700));
    const response = getAIResponse(msg);
    setTyping(false);

    const aiMsg: ChatMessage = { id: generateId(), text: response, isUser: false, timestamp: new Date() };
    setMessages((prev) => [...prev, aiMsg]);
  }

  return (
    <div className="bg-white rounded-2xl border border-green-100 shadow-xl overflow-hidden flex flex-col max-w-3xl mx-auto" style={{ height: "640px" }}>
      {/* Header */}
      <div className="bg-gradient-to-r from-green-700 to-green-500 p-5 flex items-center gap-4 flex-shrink-0">
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl">🌱</div>
        <div className="flex-1">
          <h3 className="text-white font-serif font-semibold text-lg">AgriSense AI</h3>
          <div className="flex items-center gap-2 text-green-100 text-xs mt-0.5">
            <span className="w-2 h-2 rounded-full bg-green-300 animate-pulse" />
            {t.chatbot.online}
          </div>
        </div>
        <div className="text-white/60 text-xs text-right">
          <div>Trained on</div>
          <div className="font-bold text-white">200+ Diseases</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50/50">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 12, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25 }}
              className={`flex gap-2.5 items-end ${msg.isUser ? "flex-row-reverse" : "flex-row"}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm ${
                  msg.isUser
                    ? "bg-gradient-to-br from-amber-400 to-amber-600 text-white"
                    : "bg-gradient-to-br from-green-400 to-green-700 text-white"
                }`}
              >
                {msg.isUser ? "👨‍🌾" : "🤖"}
              </div>
              <div
                className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.isUser
                    ? "bg-green-600 text-white rounded-br-sm"
                    : "bg-white text-gray-700 border border-green-100 shadow-sm rounded-bl-sm"
                }`}
              >
                {msg.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {typing && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex gap-2.5 items-end"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-green-700 flex items-center justify-center text-sm text-white">🤖</div>
              <div className="bg-white border border-green-100 shadow-sm rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="w-2 h-2 rounded-full bg-green-400 typing-dot"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      <div className="px-4 py-2 border-t border-gray-100 flex gap-2 overflow-x-auto bg-white flex-shrink-0 scrollbar-hide">
        {suggestedPrompts.slice(0, 5).map((p) => (
          <button
            key={p}
            onClick={() => { setInput(p); sendMessage(p); }}
            className="flex-shrink-0 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full text-xs text-green-700 font-medium hover:bg-green-100 transition-colors whitespace-nowrap"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100 flex gap-3 bg-white flex-shrink-0">
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder={t.chatbot.placeholder}
          className="flex-1 px-4 py-3 rounded-xl border border-green-200 text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-green-300 outline-none transition-all"
        />
        <button
          onClick={() => sendMessage()}
          disabled={!input.trim() || typing}
          className="w-12 h-12 rounded-xl bg-green-600 text-white flex items-center justify-center hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
