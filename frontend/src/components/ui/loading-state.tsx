import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function LoadingState({ message, className, size = "md" }: LoadingStateProps) {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-8 w-8",
  };
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 gap-3", className)}>
      <div className="relative">
        <Loader2 className={cn("animate-spin text-primary", sizes[size])} />
        <div className={cn("absolute inset-0 animate-pulse-glow rounded-full bg-primary/20 blur-md", sizes[size])} />
      </div>
      {message && <p className="text-sm text-muted-foreground animate-fade-in">{message}</p>}
    </div>
  );
}
