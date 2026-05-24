import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/lib/language-context";
import Navbar from "@/components/navbar/Navbar";

export const metadata: Metadata = {
  title: "AgriSense — AI Crop Disease Detection",
  description:
    "AI-powered crop disease detection and smart farming platform for Indian farmers. Upload a photo, get instant diagnosis.",
  keywords: "crop disease, agriculture, AI farming, India, mandi prices, weather advisory",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[#faf8f0] antialiased">
        <LanguageProvider>
          <Navbar />
          <main>{children}</main>
        </LanguageProvider>
      </body>
    </html>
  );
}
