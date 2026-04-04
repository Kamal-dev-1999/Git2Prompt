import * as React from "react";
import { cn } from "@/lib/cn";

/* =====================
   Card Container
   ===================== */
function NeoCard({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-base flex flex-col border-2 border-border bg-background text-foreground font-base shadow-shadow",
        className
      )}
      {...props}
    />
  );
}

/* =====================
   Card Header
   ===================== */
function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex flex-col gap-1.5 p-6", className)}
      {...props}
    />
  );
}

/* =====================
   Card Title
   ===================== */
function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn(
        "font-heading text-lg font-bold leading-none tracking-tight",
        className
      )}
      {...props}
    />
  );
}

/* =====================
   Card Description
   ===================== */
function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-sm font-base opacity-70", className)} {...props} />
  );
}

/* =====================
   Card Content
   ===================== */
function CardContent({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}

/* =====================
   Card Footer
   ===================== */
function CardFooter({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex items-center p-6 pt-0", className)}
      {...props}
    />
  );
}

export { NeoCard, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
