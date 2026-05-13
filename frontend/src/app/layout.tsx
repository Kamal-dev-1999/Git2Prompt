import type { Metadata } from "next";
import { Space_Mono, Inter } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";

const spaceMono = Space_Mono({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-space-mono",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "RepoBlueprint — Turn Any GitHub Repo Into an AI-Ready Blueprint",
  description:
    "Feed in any public GitHub repository. RepoBlueprint analyzes the codebase using Gemini 1.5 Pro and generates a hyper-detailed master prompt that another AI can use to rebuild it from scratch.",
  keywords: [
    "GitHub",
    "AI",
    "code analysis",
    "blueprint",
    "prompt engineering",
    "Gemini",
    "repository",
  ],
  authors: [{ name: "RepoBlueprint" }],
  openGraph: {
    title: "RepoBlueprint — Reproducibility Engine",
    description:
      "Turn any GitHub repository into an AI-ready master blueprint.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${spaceMono.variable} ${inter.variable}`}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
