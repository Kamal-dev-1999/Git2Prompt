"use client";

import React, { useEffect, useRef, useState } from "react";
import { Terminal } from "lucide-react";

export interface LogEntry {
  id: string;
  timestamp: string;
  prefix: string;
  message: string;
  type: "system" | "info" | "success" | "error" | "data";
}

interface AnalysisConsoleProps {
  logs: LogEntry[];
  isActive: boolean;
}

const prefixColors: Record<LogEntry["type"], string> = {
  system: "text-main",
  info: "text-[#60A5FA]",
  success: "text-accent",
  error: "text-red-400",
  data: "text-[#C084FC]",
};

export function createLog(
  prefix: string,
  message: string,
  type: LogEntry["type"] = "system"
): LogEntry {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    timestamp: new Date().toLocaleTimeString("en-US", { hour12: false }),
    prefix,
    message,
    type,
  };
}

/* Demo logs for idle/showcase mode */
export function getDemoLogs(): LogEntry[] {
  return [
    createLog("SYS", "REPOBLUEPRINT ENGINE v1.0.0 INITIALIZED", "system"),
    createLog("SYS", "AWAITING TARGET REPOSITORY INPUT...", "info"),
    createLog("SYS", "GEMINI 1.5 PRO CONTEXT ENGINE: STANDBY", "info"),
    createLog("SYS", 'TYPE A GITHUB URL AND HIT "ANALYZE" TO BEGIN', "system"),
  ];
}

export default function AnalysisConsole({
  logs,
  isActive,
}: AnalysisConsoleProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (!isActive) return;
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 530);
    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className="w-full max-w-4xl mx-auto px-4">
      <div className="border-2 border-border rounded-base shadow-shadow-md overflow-hidden">
        {/* Console Title Bar */}
        <div className="bg-foreground text-background px-4 py-2 flex items-center justify-between border-b-2 border-border">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4" strokeWidth={3} />
            <span className="font-heading text-xs font-bold tracking-wider">
              ANALYSIS_CONSOLE.exe
            </span>
          </div>
          <div className="flex items-center gap-3">
            {isActive && (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-foreground border-2 border-background animate-spin-block" />
                <span className="font-mono text-[10px] tracking-wider text-main">
                  PROCESSING
                </span>
              </div>
            )}
            <div className="flex gap-1.5">
              <div className="w-3 h-3 bg-red-500 border border-background/30" />
              <div className="w-3 h-3 bg-main border border-background/30" />
              <div className="w-3 h-3 bg-accent border border-background/30" />
            </div>
          </div>
        </div>

        {/* Console Body */}
        <div
          ref={scrollRef}
          className="bg-[#0d1117] text-[#e6edf3] p-4 h-64 overflow-y-auto font-mono text-sm leading-relaxed"
        >
          {logs.map((log, i) => (
            <div key={log.id} className="flex gap-0 mb-1">
              <span className="text-[#8B949E] shrink-0 w-20">
                {log.timestamp}
              </span>
              <span
                className={`shrink-0 font-bold ${prefixColors[log.type]}`}
              >
                [{log.prefix}]
              </span>
              <span className="ml-2 break-all">{log.message}</span>
            </div>
          ))}
          {isActive && (
            <div className="flex gap-0 mt-1">
              <span className="text-[#8B949E] shrink-0 w-20">
                {new Date().toLocaleTimeString("en-US", { hour12: false })}
              </span>
              <span className="text-main font-bold">[SYS]</span>
              <span className="ml-2">
                █{" "}
                <span
                  className={`inline-block w-2 h-4 bg-main align-middle ${
                    showCursor ? "opacity-100" : "opacity-0"
                  }`}
                />
              </span>
            </div>
          )}
        </div>

        {/* Console Status Bar */}
        <div className="bg-[#161b22] border-t-2 border-border px-4 py-1.5 flex items-center justify-between font-mono text-[10px] tracking-wider">
          <span className="text-[#8B949E]">
            {isActive ? "STATUS: ANALYZING" : "STATUS: READY"}
          </span>
          <span className="text-[#8B949E]">{logs.length} ENTRIES</span>
        </div>
      </div>
    </div>
  );
}
