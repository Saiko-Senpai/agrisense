"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { DiseaseResult as DiseaseResultType, ChatMessage, Language } from "@/types";
import { useLanguage } from "@/lib/language-context";
import { getAIResponse, generateId } from "@/lib/chatbot";
import { Send } from "lucide-react";

interface Props {
  result: DiseaseResultType;
  onReset: () => void;
}

const FOLLOW_UPS_LANG: Record<Language, string[]> = {
  en: [
    "Can this spread?",
    "Best pesticide?",
    "Organic treatment?",
    "Prevention tips?",
    "How dangerous?",
  ],
  hi: [
    "क्या यह फैल सकता है?",
    "सबसे अच्छा कीटनाशक?",
    "जैविक उपचार?",
    "बचाव के उपाय?",
    "यह कितना खतरनाक है?",
  ],
  bn: [
    "এটি কি ছড়াতে পারে?",
    "সেরা কীটনাশক?",
    "জৈব চিকিৎসা?",
    "প্রতিরোধের টিপস?",
    "এটি কতটা বিপজ্জনক?",
  ],
};

const labels: Record<Language, {
  chatTitle: string;
  suggested: string;
  newScan: string;
  welcome: (disease: string, pathogen: string, confidence: number) => string;
  scanning: string;
  defaultWelcome: string;
}> = {
  en: {
    chatTitle: "Chat with AI Specialist",
    suggested: "Suggested follow-up questions:",
    newScan: "New Scan",
    welcome: (disease: string, pathogen: string, confidence: number) => 
      `I have diagnosed this crop with **${disease}** (${pathogen}) with a confidence of **${confidence}%**. I have outlined a treatment and prevention plan above. What questions do you have about managing this disease, treatment options, or organic solutions?`,
    scanning: "AI is thinking...",
    defaultWelcome: "What would you like to know about this crop disease?"
  },
  hi: {
    chatTitle: "एआई विशेषज्ञ से चैट करें",
    suggested: "सुझाए गए अनुवर्ती प्रश्न:",
    newScan: "नया स्कैन",
    welcome: (disease: string, pathogen: string, confidence: number) => 
      `मैंने इस फसल में **${confidence}%** विश्वास के साथ **${disease}** (${pathogen}) का निदान किया है। मैंने ऊपर एक पूर्ण उपचार और रोकथाम योजना तैयार की है। इस बीमारी के प्रबंधन, उपचार के विकल्पों या जैविक समाधानों के बारे में आपके क्या प्रश्न हैं?`,
    scanning: "एआई सोच रहा है...",
    defaultWelcome: "आप इस फसल रोग के बारे में क्या जानना चाहते हैं?"
  },
  bn: {
    chatTitle: "এআই বিশেষজ্ঞের সাথে চ্যাট করুন",
    suggested: "প্রস্তাবিত ফলো-আপ প্রশ্ন:",
    newScan: "নতুন স্ক্যান",
    welcome: (disease: string, pathogen: string, confidence: number) => 
      `আমি **${confidence}%** নিশ্চিততার সাথে এই ফসলে **${disease}** (${pathogen}) রোগ সনাক্ত করেছি। আমি উপরে একটি চিকিৎসা এবং প্রতিরোধ পরিকল্পনা তৈরি করেছি। এই রোগ নিয়ন্ত্রণ, প্রতিকারের ব্যবস্থা বা জৈব উপায়ে সমাধানের বিষয়ে আপনার কি কি প্রশ্ন আছে?`,
    scanning: "এআই চিন্তা করছে...",
    defaultWelcome: "আপনি এই ফসলের রোগ সম্পর্কে কি জানতে চান?"
  }
};

function parseMarkdown(text: string): string {
  let html = text;
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Bullet points
  html = html.replace(/^- (.*?)$/gm, "• $1");
  // Newlines to <br />
  html = html.replace(/\n/g, "<br />");
  return html;
}

const chipColors: Record<string, string> = {
  "chip-red": "bg-red-50 text-red-700 border border-red-200",
  "chip-green": "bg-green-50 text-green-700 border border-green-200",
  "chip-blue": "bg-blue-50 text-blue-700 border border-blue-200",
  "chip-yellow": "bg-amber-50 text-amber-700 border border-amber-200",
};

export default function DiseaseResult({ result, onReset }: Props) {
  const router = useRouter();
  const { lang, t } = useLanguage();
  const [confWidth, setConfWidth] = useState(0);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const t = setTimeout(() => setConfWidth(result.confidence), 300);
    return () => clearTimeout(t);
  }, [result.confidence]);

  // Set up welcome message based on language and result
  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        text: labels[lang].welcome(result.disease, result.pathogen, result.confidence),
        isUser: false,
        timestamp: new Date(),
      }
    ]);
  }, [result, lang]);

  // Auto scroll
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth"
      });
    }
  }, [messages, typing]);

  const handleSend = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || typing) return;
    setInput("");

    const userMsg: ChatMessage = {
      id: generateId(),
      text: msg,
      isUser: true,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMsg]);
    setTyping(true);

    try {
      // Build conversation history excluding the welcome message
      const history = messages
        .filter((m) => m.id !== "welcome")
        .map((m) => ({
          role: m.isUser ? "user" : "assistant",
          content: m.text,
        }));

      // Enrich context with detailed disease, pathogen, and treatment plan details
      const cropName = result.crop || "Crop";
      const diseaseInfo = `Crop: ${cropName}. Disease: ${result.disease} (Pathogen: ${result.pathogen}, Confidence: ${result.confidence}%). Stage: ${result.stage}. Description: ${result.text.replace(/<[^>]*>/g, "")}. Recommended Treatment Plan: ${result.treatment.join("; ")}. Prevention Measures: ${result.prevention.join("; ")}.`;

      const response = await fetch("http://localhost:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: msg,
          crop_context: cropName,
          disease_context: diseaseInfo,
          conversation_history: history,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const resData = await response.json();
      if (resData.success && resData.data && resData.data.reply) {
        const aiMsg: ChatMessage = {
          id: generateId(),
          text: resData.data.reply,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (err) {
      console.error("Failed to fetch backend chat reply, using mock fallback:", err);
      const aiResponseText = getAIResponse(msg);
      const aiMsg: ChatMessage = {
        id: generateId(),
        text: aiResponseText,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-green-100 shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-700 to-green-500 p-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-lg">🤖</div>
          <div>
            <div className="text-white font-semibold text-sm">AgriSense AI</div>
            <div className="text-green-100 text-xs">Agricultural Disease Expert</div>
          </div>
        </div>
        <button
          onClick={onReset}
          className="px-3 py-1 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer"
        >
          🔄 {labels[lang].newScan}
        </button>
      </div>

      <div className="p-5">
        {/* Chat bubble */}
        <div className="bg-green-50 border-l-4 border-green-400 rounded-r-2xl rounded-bl-2xl p-4 mb-4">
          <p
            className="text-sm text-gray-700 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: result.text }}
          />
        </div>

        {/* Disease badge */}
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="inline-flex items-center gap-1.5 bg-red-50 text-red-700 border border-red-200 px-3 py-1 rounded-full text-sm font-bold">
            🔴 {result.disease}{result.crop ? ` (${result.crop})` : ""}
          </span>
          <span className="text-xs text-gray-400 italic">{result.pathogen}</span>
        </div>

        {/* Confidence */}
        <div className="mb-4">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Confidence Score</span>
            <span className="font-bold text-green-700">{result.confidence}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-green-400 to-green-700 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${confWidth}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Chips */}
        <div className="flex flex-wrap gap-2 mb-4">
          {result.chips.map((c) => (
            <span
              key={c.t}
              className={`px-3 py-1 rounded-full text-xs font-semibold ${chipColors[c.c] ?? "bg-gray-100 text-gray-600"}`}
            >
              {c.t}
            </span>
          ))}
        </div>

        {/* Treatment / Prevention grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
          <div>
            <div className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">💊 {result.crop ? `${result.crop} ` : ""}Treatment</div>
            <ul className="space-y-1.5">
              {result.treatment.map((item) => (
                <li key={item} className="text-xs text-gray-500 leading-relaxed flex gap-2">
                  <span className="text-green-500 flex-shrink-0 mt-0.5">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">🛡️ {result.crop ? `${result.crop} ` : ""}Prevention</div>
            <ul className="space-y-1.5">
              {result.prevention.map((item) => (
                <li key={item} className="text-xs text-gray-500 leading-relaxed flex gap-2">
                  <span className="text-amber-500 flex-shrink-0 mt-0.5">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Chat Specialist Section */}
        <div className="mt-6 pt-6 border-t border-green-100 flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-serif font-semibold text-green-800 flex items-center gap-1.5">
              💬 {labels[lang].chatTitle}
            </span>
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </div>

          {/* Messages Thread */}
          <div 
            ref={chatContainerRef}
            className="flex flex-col gap-3 max-h-[220px] overflow-y-auto p-3 bg-gray-50/70 border border-green-50/50 rounded-xl scrollbar-thin"
          >
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className={`flex gap-2 items-end ${msg.isUser ? "flex-row-reverse" : "flex-row"}`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs shadow-sm ${
                      msg.isUser
                        ? "bg-gradient-to-br from-amber-400 to-amber-600 text-white"
                        : "bg-gradient-to-br from-green-400 to-green-700 text-white"
                    }`}
                  >
                    {msg.isUser ? "👨‍🌾" : "🤖"}
                  </div>
                  <div
                    className={`max-w-[82%] px-3.5 py-2 rounded-xl text-xs leading-relaxed shadow-sm ${
                      msg.isUser
                        ? "bg-green-600 text-white rounded-br-none"
                        : "bg-white text-gray-700 border border-green-100 rounded-bl-none"
                    }`}
                  >
                    <span dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.text) }} />
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing indicator */}
            <AnimatePresence>
              {typing && (
                <motion.div
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex gap-2 items-end"
                >
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-400 to-green-700 flex items-center justify-center text-xs text-white shadow-sm">🤖</div>
                  <div className="bg-white border border-green-100 rounded-xl rounded-bl-none px-3.5 py-2.5 shadow-sm">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <span
                          key={i}
                          className="w-1.5 h-1.5 rounded-full bg-green-400 typing-dot"
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

          {/* Follow-ups */}
          <div>
            <p className="text-[11px] text-gray-400 mb-2">{labels[lang].suggested}</p>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {FOLLOW_UPS_LANG[lang].map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  disabled={typing}
                  className="px-2.5 py-1 bg-white border border-gray-200 hover:border-green-300 hover:bg-green-50 hover:text-green-700 disabled:opacity-50 disabled:hover:bg-white disabled:hover:border-gray-200 disabled:hover:text-gray-600 rounded-full text-[11px] text-gray-600 transition-all cursor-pointer"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <div className="flex gap-2 items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              disabled={typing}
              placeholder={t.chatbot.placeholder}
              className="flex-1 px-3 py-2 rounded-xl border border-green-200 text-xs bg-gray-50 focus:bg-white focus:ring-2 focus:ring-green-200 outline-none transition-all disabled:opacity-50"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || typing}
              className="w-9 h-9 rounded-xl bg-green-600 text-white flex items-center justify-center hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95 flex-shrink-0"
            >
              <Send size={14} />
            </button>
          </div>

          {/* Reset link below the chat */}
          <div className="text-center mt-1">
            <button 
              onClick={onReset}
              className="text-[11px] text-gray-400 hover:text-green-600 underline transition-all cursor-pointer bg-transparent border-none outline-none"
            >
              Scan a different crop
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
