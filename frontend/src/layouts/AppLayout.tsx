import { Outlet } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { BrainCircuit, Github, Linkedin } from "lucide-react";

export default function AppLayout() {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col">
          <header className="h-14 flex items-center justify-between border-b border-border/50 px-4 bg-card/50 backdrop-blur-md sticky top-0 z-30">
            <div className="flex items-center gap-3">
              <SidebarTrigger className="mr-1" />
              <div className="flex items-center gap-2">
                <BrainCircuit className="h-5 w-5 text-primary" />
                <span className="text-sm font-semibold tracking-tight text-foreground hidden sm:inline">
                  InsightCopilot<span className="text-primary ml-0.5">AI</span>
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium text-primary">
                IC
              </div>
            </div>
          </header>
          <main className="flex-1 p-6 overflow-auto">
            <Outlet />
          </main>
          <footer className="border-t border-border/50 bg-card/30 px-4 py-3">
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <span>Creado por <span className="font-medium text-foreground">Bruno San Martin</span></span>
              <span className="opacity-40">·</span>
              <a href="https://github.com/SanMaBruno" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-foreground transition-colors">
                <Github className="h-3.5 w-3.5" />
                GitHub
              </a>
              <span className="opacity-40">·</span>
              <a href="https://www.linkedin.com/in/sanmabruno/" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-foreground transition-colors">
                <Linkedin className="h-3.5 w-3.5" />
                LinkedIn
              </a>
            </div>
          </footer>
        </div>
      </div>
    </SidebarProvider>
  );
}
