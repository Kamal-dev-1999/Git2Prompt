"use client";

import React, { useEffect, useState } from "react";
import { Check } from "lucide-react";

interface NeoToastProps {
  message: string;
  show: boolean;
  onClose: () => void;
  duration?: number;
}

export default function NeoToast({
  message,
  show,
  onClose,
  duration = 3000,
}: NeoToastProps) {
  const [isLeaving, setIsLeaving] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      setIsLeaving(false);

      const timer = setTimeout(() => {
        setIsLeaving(true);
        setTimeout(() => {
          setIsVisible(false);
          onClose();
        }, 300);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [show, duration, onClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div
        className={`
          flex items-center gap-3
          bg-accent text-accent-foreground
          border-4 border-border
          shadow-shadow-lg
          rounded-base
          px-5 py-3
          font-heading font-bold text-sm tracking-wider
          ${isLeaving ? "animate-slide-out" : "animate-slide-in"}
        `}
      >
        <div className="w-6 h-6 bg-foreground text-background flex items-center justify-center border-2 border-border">
          <Check className="w-4 h-4" strokeWidth={3} />
        </div>
        {message}
      </div>
    </div>
  );
}
