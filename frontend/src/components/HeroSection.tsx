"use client";

import React from "react";
import { Zap, GitBranch, FileCode2 } from "lucide-react";

export default function HeroSection() {
  return (
    <section className="w-full py-16 md:py-24 px-4">
      <div className="max-w-4xl mx-auto text-center">
        {/* Decorative badge */}
        <div className="inline-flex items-center gap-2 mb-6 bg-main text-main-foreground border-2 border-border px-4 py-2 rounded-base shadow-shadow font-heading text-xs font-bold tracking-widest uppercase">
          <Zap className="w-4 h-4" strokeWidth={3} />
          AI-POWERED CODE ANALYSIS
        </div>

        {/* Main heading */}
        <h1 className="font-heading font-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl leading-[1.05] tracking-tight uppercase mb-6 text-foreground">
          TURN ANY{" "}
          <span className="bg-main text-main-foreground px-2 py-1 border-2 border-border inline-block -rotate-1 shadow-shadow">
            GITHUB REPO
          </span>{" "}
          INTO AN AI-READY BLUEPRINT
        </h1>

        {/* Subtitle */}
        <p className="font-base text-lg md:text-xl max-w-2xl mx-auto mb-8 opacity-80 leading-relaxed">
          Feed in any public repository. Get a hyper-detailed master prompt that
          another AI can use to{" "}
          <strong className="underline decoration-main decoration-4 underline-offset-4">
            rebuild it from scratch
          </strong>
          .
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-3">
          {[
            { icon: GitBranch, label: "REPO ANALYSIS" },
            { icon: FileCode2, label: "CODE MAPPING" },
            { icon: Zap, label: "GEMINI 1.5 PRO" },
          ].map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="flex items-center gap-2 bg-secondary-background border-2 border-border rounded-base px-4 py-2 font-heading text-xs font-bold tracking-wider"
            >
              <Icon className="w-4 h-4" strokeWidth={2.5} />
              {label}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
