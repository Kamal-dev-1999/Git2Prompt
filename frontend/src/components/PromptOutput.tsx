"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check, FileText, ArrowLeft } from "lucide-react";
import { NeoButton } from "@/components/ui/NeoButton";
import {
  NeoCard,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/NeoCard";
import NeoToast from "@/components/NeoToast";

interface PromptOutputProps {
  markdown: string;
  repoName?: string;
  onReset: () => void;
}

export default function PromptOutput({
  markdown,
  repoName,
  onReset,
}: PromptOutputProps) {
  const [copied, setCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setShowToast(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = markdown;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      setCopied(true);
      setShowToast(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <>
      <div className="w-full max-w-4xl mx-auto px-4 pb-16">
        {/* Action bar */}
        <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
          <NeoButton variant="neutral" size="sm" onClick={onReset}>
            <ArrowLeft className="w-4 h-4" strokeWidth={3} />
            ANALYZE ANOTHER
          </NeoButton>

          <NeoButton
            variant={copied ? "noShadow" : "default"}
            size="lg"
            onClick={handleCopy}
            className={copied ? "bg-accent" : ""}
          >
            {copied ? (
              <>
                <Check className="w-5 h-5" strokeWidth={3} />
                COPIED!
              </>
            ) : (
              <>
                <Copy className="w-5 h-5" strokeWidth={3} />
                COPY MASTER BLUEPRINT
              </>
            )}
          </NeoButton>
        </div>

        {/* Output card */}
        <NeoCard className="shadow-shadow-md">
          <CardHeader className="bg-accent border-b-2 border-border rounded-t-base">
            <CardTitle className="text-accent-foreground text-xl flex items-center gap-2">
              <FileText className="w-5 h-5" strokeWidth={3} />
              MASTER BLUEPRINT
              {repoName && (
                <span className="ml-2 bg-foreground text-background px-2 py-0.5 text-sm rounded-base">
                  {repoName}
                </span>
              )}
            </CardTitle>
          </CardHeader>

          <CardContent className="pt-6">
            <div className="prose-neo max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    const codeString = String(children).replace(/\n$/, "");

                    if (match) {
                      return (
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          customStyle={{
                            border: "2px solid var(--border)",
                            borderRadius: "var(--border-radius)",
                            boxShadow: "var(--shadow)",
                            margin: "1em 0",
                          }}
                        >
                          {codeString}
                        </SyntaxHighlighter>
                      );
                    }

                    return (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {markdown}
              </ReactMarkdown>
            </div>
          </CardContent>
        </NeoCard>

        {/* Word count */}
        <div className="mt-4 text-center font-mono text-xs tracking-wider opacity-50">
          {markdown.split(/\s+/).length.toLocaleString()} WORDS •{" "}
          {markdown.length.toLocaleString()} CHARACTERS
        </div>
      </div>

      <NeoToast
        message="BLUEPRINT COPIED TO CLIPBOARD!"
        show={showToast}
        onClose={() => setShowToast(false)}
      />
    </>
  );
}
