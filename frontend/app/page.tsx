import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ShieldAlert, BrainCircuit, Lock, ArrowRight, ShieldCheck, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="relative min-h-screen pt-32 pb-20 overflow-hidden">
      {/* Premium Background */}
      <div className="premium-bg" />

      <main className="container relative z-10 mx-auto px-4 text-center">
        {/* Floating Badge */}
        <div className="animate-slide-up flex justify-center mb-8">
          <div className="glass px-6 py-2 rounded-full flex items-center gap-2 border-primary/20 bg-primary/5">
            <Zap className="w-4 h-4 text-primary animate-pulse" />
            <span className="text-xs font-bold tracking-widest uppercase text-primary">Advanced AI Scrutiny 2.0</span>
          </div>
        </div>

        {/* Hero Title */}
        <div className="animate-slide-up stagger-1 max-w-4xl mx-auto mb-12">
          <h1 className="text-6xl md:text-8xl font-display font-extrabold tracking-tighter leading-tight mb-6">
            Scam Detection <br />
            <span className="text-gradient">Redefined.</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground font-medium max-w-2xl mx-auto leading-relaxed">
            Protect your digital identity with military-grade linguistic forensic AI.
            Identify fraud before the first click.
          </p>
        </div>

        {/* CTAs */}
        <div className="animate-slide-up stagger-2 flex flex-col sm:flex-row gap-6 justify-center mb-24">
          <Link href="/analyze">
            <Button size="lg" className="h-16 px-10 rounded-2xl text-lg font-bold bg-primary hover:bg-primary/90 shadow-2xl shadow-primary/40 group transition-all duration-500 hover:scale-105 active:scale-95">
              Secure Analysis <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
          <Link href="/demo">
            <Button variant="outline" size="lg" className="glass h-16 px-10 rounded-2xl text-lg font-bold hover:bg-white/10 transition-all duration-500 hover:scale-105 active:scale-95">
              Live Demo
            </Button>
          </Link>
        </div>

        {/* Visual Showcase - Scanner Animation */}
        <div className="animate-slide-up stagger-3 max-w-5xl mx-auto">
          <div className="relative glass-card overflow-hidden p-0 animate-float bg-black/5 dark:bg-white/5">
            <div className="scan-line" />
            <div className="grid grid-cols-1 md:grid-cols-2">
              <div className="p-8 text-left border-r border-border/50">
                <div className="flex items-center gap-2 mb-4 text-primary">
                  <ShieldCheck className="w-5 h-5" />
                  <span className="text-sm font-bold uppercase tracking-wider">Analysis Engine</span>
                </div>
                <div className="space-y-3">
                  <div className="h-2 w-3/4 bg-primary/20 rounded-full" />
                  <div className="h-2 w-full bg-primary/10 rounded-full" />
                  <div className="h-2 w-1/2 bg-primary/10 rounded-full" />
                </div>
                <div className="mt-8">
                  <p className="text-sm text-muted-foreground italic">&quot;Heuristic logic matched 15+ scam signals in 0.2ms...&quot;</p>
                </div>
              </div>
              <div className="p-8 bg-primary/[0.02] flex items-center justify-center">
                <div className="text-center">
                  <div className="text-5xl font-black text-primary mb-2">99.8%</div>
                  <div className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Detection Accuracy</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-32">
          <FeatureItem
            icon={<ShieldAlert className="w-8 h-8 text-danger" />}
            title="Url Forensics"
            description="Deep analysis of subdomain hijacking, TLD risk, and path obfuscation."
          />
          <FeatureItem
            icon={<BrainCircuit className="w-8 h-8 text-warning" />}
            title="Grammar DNA"
            description="Identifying the unique 'linguistic signature' of automated scam campaigns."
          />
          <FeatureItem
            icon={<Lock className="w-8 h-8 text-safe" />}
            title="Privacy Zero"
            description="We never store your content. Pure encrypted transient analysis."
          />
        </div>
      </main>
    </div>
  );
}

function FeatureItem({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="glass-card hover:-translate-y-2 transition-transform duration-500 group">
      <div className="mb-6 h-16 w-16 glass rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-500">
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-3 tracking-tight">{title}</h3>
      <p className="text-muted-foreground leading-relaxed leading-relaxed">{description}</p>
    </div>
  );
}
