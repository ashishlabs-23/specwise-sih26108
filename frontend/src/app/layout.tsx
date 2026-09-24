import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/context/LanguageContext";

export const metadata: Metadata = {
  title: "SpecWise — BIS Standards Recommendation Engine | SIH26108",
  description:
    "Smart procurement decision support system for finding applicable Indian Standards (BIS) from tender specifications with verified evidence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 antialiased selection:bg-blue-100 selection:text-blue-900">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
