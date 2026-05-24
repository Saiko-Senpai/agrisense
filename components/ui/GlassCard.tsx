import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export default function GlassCard({ children, className = "", hover = false }: GlassCardProps) {
  return (
    <div
      className={`
        glass rounded-2xl shadow-lg shadow-green-900/10
        ${hover ? "transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-green-900/15 cursor-pointer" : ""}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
