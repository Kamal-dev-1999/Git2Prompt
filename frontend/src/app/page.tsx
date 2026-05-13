"use client";
import React, { useState, useCallback, useRef } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import RepoSearch from "@/components/RepoSearch";
import AnalysisConsole, {
  createLog,
  getDemoLogs,
  type LogEntry,
} from "@/components/AnalysisConsole";
import PromptOutput from "@/components/PromptOutput";
import { NeoButton } from "@/components/ui/NeoButton";
import { NeoCard, CardContent } from "@/components/ui/NeoCard";
import { AlertTriangle, RotateCcw, Settings } from "lucide-react";
import SettingsCard from "@/components/SettingsCard";

type AppState = "idle" | "analyzing" | "complete" | "error";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [logs, setLogs] = useState<LogEntry[]>(getDemoLogs());
  const [blueprint, setBlueprint] = useState("");
  const [repoName, setRepoName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const analyzeAbortRef = useRef<AbortController | null>(null);

  const addLog = useCallback(
    (prefix: string, message: string, type: LogEntry["type"] = "system") => {
      setLogs((prev) => [...prev, createLog(prefix, message, type)]);
    },
    []
  );

  /* ===================================
     REAL ANALYSIS (SSE Stream)
     =================================== */
  const runRealAnalysis = useCallback(
    async (repoUrl: string) => {
      // Parse repo name
      const match = repoUrl.match(/github\.com\/([^/]+\/[^/]+)/);
      const name = match ? match[1] : repoUrl;
      setRepoName(name);

      const abortController = new AbortController();
      analyzeAbortRef.current = abortController;

      try {
        const userGeminiKey = localStorage.getItem("repo_blueprint_user_key");
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (userGeminiKey) {
          headers["x-user-gemini-key"] = userGeminiKey;
        }

        const response = await fetch("/api/analyze", {
          method: "POST",
          headers,
          body: JSON.stringify({ repoUrl }),
          signal: abortController.signal,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          
          if (response.status === 429) {
            throw new Error(`[429] Rate limit exceeded. ${errData.message || 'Please wait or enter your personal API key.'}`);
          }
          if (response.status === 401) {
            throw new Error(`[401] Unauthorized. ${errData.message || 'Your personal API key may be invalid.'}`);
          }
          
          throw new Error(errData.error || `HTTP ${response.status}`);
        }

        if (!response.body) {
          throw new Error("No response body returned from server");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || ""; // Keep the incomplete part

          for (const part of parts) {
            const eventMatch = part.match(/event: (.*)\n/);
            const dataMatch = part.match(/data: (.*)/);

            if (eventMatch && dataMatch) {
              const eventType = eventMatch[1].trim();
              const eventData = JSON.parse(dataMatch[1].trim());

              if (eventType === "progress") {
                const logType = eventData.message.includes("[ERROR") ? "error" :
                                eventData.message.includes("✓") ? "success" :
                                eventData.message.includes("TOKEN") || eventData.message.includes("FILE") || eventData.message.includes("OBJECT") ? "data" :
                                eventData.message.includes("[GIT]") || eventData.message.includes("[AI]") ? "info" : "system";
                
                const prefixMatch = eventData.message.match(/^\[(.*?)\]/);
                const prefix = prefixMatch ? prefixMatch[1] : "SYS";
                const msg = eventData.message.replace(/^\[.*?\]\s*/, "");
                
                addLog(prefix, msg, logType);
              } else if (eventType === "blueprint_chunk") {
                // If we want real-time typing effect for the blueprint, we can append to state
                // But in this design, we wait for full output to show.
              } else if (eventType === "blueprint") {
                setBlueprint(eventData.content);
                setAppState("complete");
              } else if (eventType === "error") {
                if (eventData.code === 401) {
                  throw new Error(`[401] Unauthorized: ${eventData.message}`);
                }
                throw new Error(eventData.message);
              } else if (eventType === "done") {
                // Stream finished
                break;
              }
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          addLog("SYS", "ANALYSIS ABORTED BY USER", "error");
        } else {
          throw err;
        }
      } finally {
        analyzeAbortRef.current = null;
      }
    },
    [addLog]
  );

  const handleAnalyze = useCallback(
    async (repoUrl: string) => {
      setAppState("analyzing");
      setLogs([createLog("SYS", "NEW ANALYSIS SESSION STARTED", "system")]);
      setBlueprint("");
      setErrorMessage("");

      try {
        await runRealAnalysis(repoUrl);
      } catch (err: unknown) {
        setErrorMessage(
          err instanceof Error ? err.message : "UNKNOWN ERROR OCCURRED"
        );
        setAppState("error");
      }
    },
    [runRealAnalysis]
  );

  const handleReset = useCallback(() => {
    if (analyzeAbortRef.current) {
      analyzeAbortRef.current.abort();
    }
    setAppState("idle");
    setLogs(getDemoLogs());
    setBlueprint("");
    setRepoName("");
    setErrorMessage("");
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col">
        {/* IDLE STATE */}
        {appState === "idle" && (
          <>
            <HeroSection />
            <RepoSearch onAnalyze={handleAnalyze} />
            <SettingsCard />
            <div className="mt-12">
              <AnalysisConsole logs={logs} isActive={false} />
            </div>
          </>
        )}

        {/* ANALYZING STATE */}
        {appState === "analyzing" && (
          <div className="flex-1 flex flex-col items-center justify-center py-12">
            <div className="mb-8 text-center">
              <h2 className="font-heading font-black text-2xl md:text-3xl uppercase tracking-tight mb-2">
                ANALYZING REPOSITORY
              </h2>
              <p className="font-mono text-sm opacity-60">
                {repoName || "PROCESSING..."}
              </p>
            </div>
            <AnalysisConsole logs={logs} isActive={true} />
            <div className="mt-6">
              <NeoButton variant="neutral" size="sm" onClick={handleReset}>
                CANCEL
              </NeoButton>
            </div>
          </div>
        )}

        {/* COMPLETE STATE */}
        {appState === "complete" && (
          <div className="flex-1 py-8">
            <PromptOutput
              markdown={blueprint}
              repoName={repoName}
              onReset={handleReset}
            />
          </div>
        )}

        {/* ERROR STATE */}
        {appState === "error" && (
          <div className="flex-1 flex items-center justify-center py-12 px-4">
            <NeoCard className="max-w-lg w-full shadow-shadow-md">
              <div className="bg-red-500 text-white p-4 border-b-2 border-border rounded-t-base flex items-center gap-2">
                <AlertTriangle className="w-6 h-6" strokeWidth={3} />
                <span className="font-heading font-bold text-lg tracking-wider">
                  ANALYSIS FAILED
                </span>
              </div>
              <CardContent className="pt-6">
                <p className="font-mono text-sm mb-4 bg-red-50 border-2 border-border p-4 rounded-base text-black font-bold">
                  {errorMessage || "An unexpected error occurred."}
                </p>
                <div className="flex gap-4 w-full">
                  <NeoButton
                    onClick={handleReset}
                    className="flex-1"
                    size="lg"
                  >
                    <RotateCcw className="w-5 h-5" strokeWidth={3} />
                    TRY AGAIN
                  </NeoButton>
                  
                  {(errorMessage.includes("429") || errorMessage.includes("401") || errorMessage.includes("API Key")) && (
                    <NeoButton
                      variant="neutral"
                      onClick={() => {
                        handleReset();
                        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                      }}
                      className="flex-none px-4"
                      size="lg"
                      title="Enter Personal Key"
                    >
                      <Settings className="w-5 h-5" strokeWidth={3} />
                    </NeoButton>
                  )}
                </div>
              </CardContent>
            </NeoCard>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-border bg-foreground text-background py-3">
        <div className="max-w-4xl mx-auto px-4 flex items-center justify-between font-mono text-xs tracking-wider">
          <span>REPOBLUEPRINT v1.0</span>
          <span className="opacity-60">POWERED BY GEMINI 1.5 PRO</span>
        </div>
      </footer>
    </div>
  );
}
