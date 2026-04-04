"use client";

import React, { useState } from "react";
import { Search, AlertTriangle, Zap } from "lucide-react";
import { NeoButton } from "@/components/ui/NeoButton";
import { NeoInput } from "@/components/ui/NeoInput";
import {
  NeoCard,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/NeoCard";

interface RepoSearchProps {
  onAnalyze: (repoUrl: string) => void;
  isLoading?: boolean;
}

function extractRepoInfo(url: string): { owner: string; repo: string } | null {
  const patterns = [
    /^https?:\/\/github\.com\/([^/]+)\/([^/]+?)(\.git)?$/,
    /^https?:\/\/github\.com\/([^/]+)\/([^/]+?)(\/)?$/,
    /^github\.com\/([^/]+)\/([^/]+?)(\/)?$/,
    /^([^/]+)\/([^/]+)$/,
  ];

  for (const pattern of patterns) {
    const match = url.trim().match(pattern);
    if (match) {
      return { owner: match[1], repo: match[2] };
    }
  }
  return null;
}

export default function RepoSearch({ onAnalyze, isLoading }: RepoSearchProps) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!url.trim()) {
      setError("ENTER A REPOSITORY URL");
      return;
    }

    const repoInfo = extractRepoInfo(url);
    if (!repoInfo) {
      setError("INVALID GITHUB URL FORMAT. USE: github.com/owner/repo");
      return;
    }

    onAnalyze(url.trim());
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <NeoCard className="shadow-shadow-md">
        <CardHeader className="bg-main border-b-2 border-border rounded-t-base">
          <CardTitle className="text-main-foreground text-xl flex items-center gap-2">
            <Search className="w-5 h-5" strokeWidth={3} />
            REPOSITORY INPUT
          </CardTitle>
          <CardDescription className="text-main-foreground/70 font-mono text-xs">
            PASTE A PUBLIC GITHUB REPOSITORY URL BELOW
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label
                htmlFor="repo-url-input"
                className="font-heading text-xs font-bold tracking-wider uppercase"
              >
                GITHUB URL
              </label>
              <NeoInput
                id="repo-url-input"
                type="text"
                placeholder="https://github.com/owner/repository"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (error) setError("");
                }}
                disabled={isLoading}
                autoComplete="url"
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-red-100 border-2 border-border text-red-800 px-4 py-2 rounded-base font-heading text-xs font-bold">
                <AlertTriangle className="w-4 h-4 shrink-0" strokeWidth={3} />
                {error}
              </div>
            )}

            <NeoButton
              type="submit"
              size="lg"
              disabled={isLoading}
              className="w-full text-base"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-main-foreground border-t-transparent animate-spin" />
                  ANALYZING...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" strokeWidth={3} />
                  ANALYZE REPOSITORY
                </>
              )}
            </NeoButton>
          </form>
        </CardContent>

        <CardFooter className="flex-col gap-1">
          <p className="font-mono text-[10px] tracking-wider opacity-50 text-center">
            SUPPORTS PUBLIC REPOSITORIES • POWERED BY GEMINI 1.5 PRO
          </p>
        </CardFooter>
      </NeoCard>

      {/* Example repos */}
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <span className="font-heading text-xs font-bold tracking-wider opacity-50">
          TRY:
        </span>
        {[
          "facebook/react",
          "vercel/next.js",
          "expressjs/express",
        ].map((repo) => (
          <button
            key={repo}
            onClick={() => setUrl(`https://github.com/${repo}`)}
            className="font-mono text-xs bg-secondary-background border-2 border-border rounded-base px-2 py-1 hover:bg-main hover:text-main-foreground transition-colors cursor-pointer"
          >
            {repo}
          </button>
        ))}
      </div>
    </div>
  );
}
