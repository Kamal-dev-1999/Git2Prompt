"use client";

import React, { useState, useEffect } from "react";
import { Cpu, ShieldCheck } from "lucide-react";

export default function Header() {
  const [hasKey, setHasKey] = useState(false);

  useEffect(() => {
    const checkKey = () => setHasKey(!!localStorage.getItem("repo_blueprint_user_key"));
    checkKey();
    window.addEventListener("api-key-updated", checkKey);
    return () => window.removeEventListener("api-key-updated", checkKey);
  }, []);

  const marqueeText =
    "REPRODUCIBILITY ENGINE // REPOBLUEPRINT ◆ REPRODUCIBILITY ENGINE // REPOBLUEPRINT ◆ ";

  return (
    <header className="w-full bg-foreground text-background border-b-4 border-border overflow-hidden select-none">
      {/* Top accent bar */}
      <div className="h-2 bg-main w-full" />

      <div className="flex items-center h-12">
        {/* Logo block */}
        <div className="flex items-center gap-2 px-4 bg-main text-main-foreground h-full border-r-4 border-border shrink-0 z-10">
          <Cpu className="w-5 h-5" strokeWidth={3} />
          <span className="font-heading font-bold text-sm tracking-wider hidden sm:inline">
            RB://
          </span>
        </div>

        {/* Marquee */}
        <div className="flex-1 overflow-hidden h-full flex items-center">
          <div className="animate-marquee whitespace-nowrap flex items-center">
            <span className="font-heading text-sm font-bold tracking-[0.2em] text-background/80">
              {marqueeText}
            </span>
            <span className="font-heading text-sm font-bold tracking-[0.2em] text-background/80">
              {marqueeText}
            </span>
          </div>
        </div>

        {/* Status blocks */}
        {hasKey && (
          <div className="flex items-center gap-2 px-3 bg-[#FACC15] text-black h-full border-l-4 border-border shrink-0">
            <ShieldCheck className="w-4 h-4" strokeWidth={3} />
            <span className="font-heading font-bold text-xs tracking-wider hidden md:inline">
              KEY ACTIVE
            </span>
          </div>
        )}

        <div className="flex items-center gap-2 px-4 bg-accent text-accent-foreground h-full border-l-4 border-border shrink-0">
          <div className="w-2 h-2 bg-foreground rounded-full" />
          <span className="font-heading text-xs font-bold tracking-wider hidden md:inline">
            ONLINE
          </span>
        </div>
      </div>
    </header>
  );
}
