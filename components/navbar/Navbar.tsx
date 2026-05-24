"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useLanguage } from "@/lib/language-context";

const navItems = [
  { href: "/", key: "home" },
  { href: "/crops", key: "cropLibrary" },
  { href: "/weather", key: "weather" },
  { href: "/assistant", key: "assistant" },
  { href: "/about", key: "about" },
] as const;

export default function Navbar() {
  const pathname = usePathname();
  const { t, cycleLang, langLabel } = useLanguage();
  const [menuOpen, setMenuOpen] = useState(false);

  const navLabels: Record<string, string> = {
    home: t.nav.home,
    cropLibrary: t.nav.cropLibrary,
    weather: t.nav.weather,
    assistant: t.nav.assistant,
    about: t.nav.about,
  };

  return (
    <>
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="sticky top-3 z-50 mx-3 md:mx-4"
      >
        <div className="backdrop-blur-xl bg-white/75 border border-green-200/60 rounded-2xl px-5 py-3.5 shadow-lg shadow-green-900/10 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-[50%_50%_50%_0] bg-gradient-to-br from-green-400 to-green-700 flex items-center justify-center text-white text-sm shadow-md group-hover:scale-110 transition-transform">
              🌿
            </div>
            <span className="font-serif font-bold text-xl text-green-800 tracking-tight">
              AgriSense
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map(({ href, key }) => {
              const active =
                href === "/" ? pathname === "/" : pathname.startsWith(href);
              return (
                <Link
                  key={key}
                  href={href}
                  className={`px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    active
                      ? "bg-green-100 text-green-800"
                      : "text-green-700/70 hover:bg-green-50 hover:text-green-800"
                  }`}
                >
                  {navLabels[key]}
                </Link>
              );
            })}
            <button
              onClick={cycleLang}
              className="ml-2 px-3 py-1.5 rounded-xl border border-amber-200 bg-amber-50 text-amber-800 text-sm font-semibold hover:bg-amber-100 transition-all duration-200"
            >
              🌐 {langLabel}
            </button>
          </div>

          {/* Mobile controls */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={cycleLang}
              className="px-3 py-1.5 rounded-xl border border-amber-200 bg-amber-50 text-amber-800 text-sm font-semibold"
            >
              🌐 {langLabel}
            </button>
            <button
              onClick={() => setMenuOpen((v) => !v)}
              className="p-2 rounded-xl text-green-700 hover:bg-green-50 transition-colors"
              aria-label="Toggle menu"
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.97 }}
              transition={{ duration: 0.18 }}
              className="mt-2 backdrop-blur-xl bg-white/90 border border-green-200/60 rounded-2xl p-3 shadow-xl shadow-green-900/10"
            >
              {navItems.map(({ href, key }) => {
                const active =
                  href === "/" ? pathname === "/" : pathname.startsWith(href);
                return (
                  <Link
                    key={key}
                    href={href}
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all mb-1 last:mb-0 ${
                      active
                        ? "bg-green-100 text-green-800"
                        : "text-green-700/70 hover:bg-green-50 hover:text-green-800"
                    }`}
                  >
                    {navLabels[key]}
                  </Link>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>
    </>
  );
}
