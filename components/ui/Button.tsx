import { ReactNode, ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "white" | "ghost";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

const variants = {
  primary:
    "bg-gradient-to-r from-green-400 to-green-700 text-white shadow-lg shadow-green-700/30 hover:shadow-green-700/50 hover:-translate-y-0.5",
  secondary:
    "bg-white/80 text-green-700 border border-green-300 hover:bg-green-50 hover:-translate-y-0.5",
  white:
    "bg-white text-green-700 font-bold hover:-translate-y-1 hover:shadow-xl",
  ghost:
    "text-green-700 hover:bg-green-100 border border-transparent hover:border-green-200",
};

const sizes = {
  sm: "px-4 py-2 text-sm",
  md: "px-6 py-3 text-sm",
  lg: "px-7 py-3.5 text-base",
};

export default function Button({
  variant = "primary",
  size = "md",
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 rounded-full font-semibold
        transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}
