"use client";

import React, { useState, useEffect } from "react";
import { KeyRound, Check, X } from "lucide-react";
import { NeoButton } from "@/components/ui/NeoButton";
import { NeoInput } from "@/components/ui/NeoInput";
import NeoToast from "@/components/NeoToast";

export default function SettingsCard() {
  const [apiKey, setApiKey] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState("");

  useEffect(() => {
    // Load existing key from localStorage
    const saved = localStorage.getItem("repo_blueprint_user_key");
    if (saved) {
      setApiKey(saved);
      setIsSaved(true);
    }
  }, []);

  const handleSave = () => {
    const trimmed = apiKey.trim();
    if (trimmed) {
      localStorage.setItem("repo_blueprint_user_key", trimmed);
      setIsSaved(true);
      
      const company = trimmed.startsWith("sk-or-") ? "OPENROUTER" : "GEMINI";
      setToastMsg(`${company} KEY SAVED`);
      
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2500);
      
      // Dispatch an event so the Header can update its badge immediately
      window.dispatchEvent(new Event("api-key-updated"));
    }
  };

  const handleClear = () => {
    localStorage.removeItem("repo_blueprint_user_key");
    setApiKey("");
    setIsSaved(false);
    setToastMsg("API KEY CLEARED");
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
    
    window.dispatchEvent(new Event("api-key-updated"));
  };

  return (
    <>
      <div className="w-full max-w-2xl mx-auto my-6 p-6 bg-[#FACC15] border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-base">
        <div className="flex items-center gap-3 mb-4 border-b-4 border-black pb-4">
          <div className="bg-white p-2 border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] rounded-base">
            <KeyRound className="w-6 h-6 text-black" strokeWidth={3} />
          </div>
          <div>
            <h3 className="font-heading font-black text-xl tracking-tight uppercase text-black">
              BYOK: Personal AI Key
            </h3>
            <p className="font-mono text-xs text-black/80 font-bold">
              Bypass server rate limits by bringing your own Gemini or OpenRouter Key.
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full relative group">
            <label className="block font-heading font-bold text-sm tracking-wider mb-2 text-black">
              AI API KEY (GEMINI OR OPENROUTER)
            </label>
            <NeoInput
              type="password"
              placeholder="AIzaSy... or sk-or-..."
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                if (isSaved) setIsSaved(false);
              }}
              className="bg-white text-black placeholder:text-gray-400 group-hover:translate-x-0 group-hover:translate-y-0"
            />
          </div>

          <div className="flex gap-2 w-full md:w-auto">
            <NeoButton 
              onClick={handleSave} 
              className={isSaved ? "bg-white text-black flex-1 md:flex-none" : "flex-1 md:flex-none"}
              disabled={!apiKey.trim() || isSaved}
            >
              {isSaved ? <><Check className="w-4 h-4"/> SAVED</> : "SAVE KEY"}
            </NeoButton>
            
            {isSaved && (
              <NeoButton variant="destructive" className="px-3" onClick={handleClear} title="Clear Key">
                <X className="w-5 h-5" strokeWidth={3} />
              </NeoButton>
            )}
          </div>
        </div>
      </div>

      <NeoToast
        message={toastMsg}
        show={showToast}
        onClose={() => setShowToast(false)}
      />
    </>
  );
}
