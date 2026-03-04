"use client"

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFraudStore } from '@/store/useFraudStore';
import {
    ArrowLeft, Check, AlertOctagon, Info, Sparkles, Scan, Eye,
    Database, FileText, AlignLeft, ShieldCheck, XCircle, SpellCheck,
    Mail, Paperclip, AlertTriangle, Smartphone, Search, Bot, User,
    Zap, Globe, ShieldAlert
} from 'lucide-react';
import Link from 'next/link';

export default function ResultsPage() {
    const router = useRouter();
    const { result, isAnalyzing, inputText } = useFraudStore();

    useEffect(() => {
        if (!isAnalyzing && !result && !inputText) {
            router.push('/analyze');
        }
    }, [isAnalyzing, result, inputText, router]);

    if (isAnalyzing) {
        return (
            <div className="relative min-h-[80vh] flex flex-col items-center justify-center p-4">
                <div className="premium-bg" />
                <div className="glass-card max-w-md w-full text-center relative overflow-hidden p-12">
                    <div className="scan-line" />
                    <div className="relative mb-8 flex justify-center">
                        <div className="h-24 w-24 glass rounded-full flex items-center justify-center animate-float">
                            <ShieldCheck className="w-12 h-12 text-primary animate-pulse" />
                        </div>
                    </div>
                    <h2 className="text-3xl font-black tracking-tight mb-2">Analyzing...</h2>
                    <p className="text-muted-foreground font-medium">Linguistic Forensic AI & API Orchestration in progress</p>
                    <div className="mt-8 space-y-2 opacity-50">
                        <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-primary w-1/2 animate-shimmer" />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!result) return null;

    const riskLevels = {
        Safe: { color: 'text-safe', bg: 'bg-safe/10', border: 'border-safe/20', icon: <Check className="w-5 h-5" />, hex: '#16a34a' },
        Suspicious: { color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/20', icon: <AlertTriangle className="w-5 h-5" />, hex: '#d97706' },
        High: { color: 'text-danger', bg: 'bg-danger/10', border: 'border-danger/20', icon: <ShieldAlert className="w-5 h-5" />, hex: '#dc2626' },
        Critical: { color: 'text-critical', bg: 'bg-critical/10', border: 'border-critical/20', icon: <AlertOctagon className="w-5 h-5" />, hex: '#9333ea' }
    };

    const level = (result.risk_level as keyof typeof riskLevels) || 'Suspicious';
    const ui = riskLevels[level] || riskLevels.Suspicious;

    const handleGoogleSearch = () => {
        const searchText = inputText || '';
        const searchQuery = `scam fraud check: ${searchText.substring(0, 200)}`;
        window.open(`https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`, '_blank');
    };

    return (
        <div className="relative min-h-screen pt-32 pb-20 overflow-hidden">
            <div className="premium-bg" />

            <main className="container relative z-10 mx-auto px-4 max-w-6xl">
                {/* Header Actions */}
                <div className="animate-slide-up flex flex-wrap items-center justify-between gap-4 mb-8">
                    <div className="flex items-center gap-4">
                        <Link href="/analyze" className="glass h-12 w-12 rounded-2xl flex items-center justify-center hover:bg-white/10 transition-all">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-3xl font-black tracking-tight">Security Verdict</h1>
                            <p className="text-muted-foreground text-sm font-medium">Analysis ID: <span className="font-mono">{Math.random().toString(36).substr(2, 9).toUpperCase()}</span></p>
                        </div>
                    </div>

                    <button
                        onClick={handleGoogleSearch}
                        className="glass px-6 py-3 rounded-2xl flex items-center gap-2 hover:bg-black/5 dark:hover:bg-white/5 transition-all group font-bold"
                    >
                        <Search className="w-4 h-4 text-primary group-hover:scale-110 transition-transform" />
                        Cross-Reference Google
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* LEFT COLUMN - THE VERDICT */}
                    <div className="lg:col-span-4 space-y-8">
                        <div className="animate-slide-up stagger-1 glass-card text-center flex flex-col items-center">
                            <div className="score-radial" style={{ '--percentage': result.risk_score, '--color': ui.hex } as any}>
                                <div className="text-center">
                                    <div className="text-4xl font-black" style={{ color: ui.hex }}>{result.risk_score}</div>
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground opacity-60">Risk Score</div>
                                </div>
                            </div>

                            <div className={`mt-6 inline-flex items-center gap-2 px-4 py-1.5 rounded-full border ${ui.bg} ${ui.color} ${ui.border} font-black text-sm uppercase tracking-widest`}>
                                {ui.icon} {level} RISK
                            </div>

                            <p className="mt-6 text-sm text-balance text-muted-foreground leading-relaxed">
                                {result.explanation.split('.')[0]}.
                            </p>

                            <div className="mt-8 w-full pt-8 border-t border-border/50 space-y-3">
                                <div className="flex items-center justify-between text-xs px-2 font-bold">
                                    <span className="text-muted-foreground uppercase tracking-widest">Confidence</span>
                                    <span className="text-foreground">{(result.confidence * 100).toFixed(0)}%</span>
                                </div>
                                <div className="h-2 w-full glass rounded-full overflow-hidden">
                                    <div className="h-full bg-primary" style={{ width: `${result.confidence * 100}%` }} />
                                </div>
                            </div>
                        </div>

                        {/* Author/Tone Card */}
                        <div className="animate-slide-up stagger-2 glass-card p-6 flex flex-col gap-4">
                            <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-2 flex items-center gap-2">
                                <Bot className="w-4 h-4" /> Linguistic Meta
                            </h4>
                            <div className="flex items-center justify-between p-3 glass rounded-2xl">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 glass rounded-xl flex items-center justify-center text-primary">
                                        {result.author_prediction === 'AI Generated' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-muted-foreground">Author</div>
                                        <div className="text-sm font-black">{result.author_prediction || 'Unknown'}</div>
                                    </div>
                                </div>
                                <div className="px-3 py-1 bg-white/10 rounded-full text-[10px] font-bold uppercase">Predicted</div>
                            </div>

                            <div className="flex items-center justify-between p-3 glass rounded-2xl">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 glass rounded-xl flex items-center justify-center text-accent">
                                        <Zap className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-muted-foreground">Primary Tone</div>
                                        <div className="text-sm font-black">{result.tone}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* RIGHT COLUMN - DETAILS */}
                    <div className="lg:col-span-8 space-y-8">

                        {/* Text Content Breakdown */}
                        <div className="animate-slide-up stagger-2 glass-card p-0 overflow-hidden">
                            <div className="bg-muted/10 px-8 py-4 border-b border-border/50 flex items-center justify-between">
                                <h3 className="font-bold flex items-center gap-2"><Scan className="w-4 h-4 text-primary" /> Visual Scan</h3>
                                <div className="flex gap-2">
                                    <div className="h-3 w-3 rounded-full bg-red-400/20" />
                                    <div className="h-3 w-3 rounded-full bg-yellow-400/20" />
                                    <div className="h-3 w-3 rounded-full bg-green-400/20" />
                                </div>
                            </div>
                            <div className="p-8">
                                <div className="relative glass p-6 rounded-2xl border-white/5 bg-black/5 dark:bg-white/5 font-medium leading-loose text-lg">
                                    <div className="scan-line !h-[2px]" />
                                    {inputText}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Grammar Forensics */}
                            <div className="animate-slide-up stagger-3 glass-card">
                                <h4 className="text-lg font-black mb-6 flex items-center gap-2">
                                    <SpellCheck className="w-6 h-6 text-primary" /> Forensics
                                </h4>
                                <div className="flex items-center gap-6 mb-8">
                                    <div className="text-5xl font-black text-gradient">{result.text_error_analysis?.score || 100}</div>
                                    <div>
                                        <div className="font-bold">Grammar Score</div>
                                        <div className="text-xs text-muted-foreground">NLP Integrity Checklist</div>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    {result.text_error_analysis?.typos?.map((typo: string, i: number) => (
                                        <div key={i} className="flex items-center gap-3 text-xs font-medium p-3 glass rounded-xl text-danger border-danger/10">
                                            <AlertTriangle className="w-3 h-3" /> {typo}
                                        </div>
                                    ))}
                                    {(!result.text_error_analysis?.typos?.length) && (
                                        <div className="flex items-center gap-3 text-xs font-medium p-3 glass rounded-xl text-safe border-safe/10">
                                            <ShieldCheck className="w-4 h-4" /> No linguistic anomalies detected
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Trust Network Comparisons */}
                            <div className="animate-slide-up stagger-3 glass-card bg-slate-900 dark:bg-black/50 overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-5">
                                    <Database className="w-32 h-32 text-white" />
                                </div>
                                <h4 className="text-lg font-black mb-6 text-white flex items-center gap-2">
                                    <Globe className="w-6 h-6 text-blue-400" /> Trust Network
                                </h4>
                                <div className="space-y-4">
                                    <div className="p-4 glass rounded-2xl border-white/5 space-y-2">
                                        <div className="flex justify-between text-xs font-bold text-white/60">
                                            <span>Global Match</span>
                                            <span>{result.similar_case_match?.similarity_score || 0}%</span>
                                        </div>
                                        <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                                            <div className="h-full bg-blue-500" style={{ width: `${result.similar_case_match?.similarity_score || 0}%` }} />
                                        </div>
                                        <p className="text-[10px] text-white/40 italic">Checking against 11 proprietary scam datasets...</p>
                                    </div>

                                    {result.bank_verification?.detected_bank && (
                                        <div className={`p-4 rounded-2xl border flex flex-col gap-2 ${result.bank_verification.is_official_domain ? 'bg-safe/5 border-safe/20' : 'bg-danger/5 border-danger/20'}`}>
                                            <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-tighter">
                                                {result.bank_verification.is_official_domain ? <Check className="w-3 h-3 text-safe" /> : <XCircle className="w-3 h-3 text-danger" />}
                                                {result.bank_verification.detected_bank}
                                            </div>
                                            <p className="text-[10px] text-white/50">{result.bank_verification.risk_reason}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Reasoning Matrix */}
                        <div className="animate-slide-up stagger-4 glass-card">
                            <h4 className="text-xl font-black mb-6">Decision Intelligence Matrix</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {result.why_fraud?.map((reason: string, i: number) => (
                                    <div key={i} className="flex gap-4 p-4 glass rounded-2xl border-danger/10">
                                        <div className="h-10 w-10 shrink-0 glass rounded-xl flex items-center justify-center text-danger">
                                            <ShieldAlert className="w-5 h-5 shadow-sm" />
                                        </div>
                                        <div>
                                            <div className="text-sm font-black leading-tight text-danger/80">Anomaly {i + 1}</div>
                                            <p className="text-xs text-muted-foreground mt-1">{reason}</p>
                                        </div>
                                    </div>
                                ))}
                                {result.counterfactual_safe_conditions?.map((cond: string, i: number) => (
                                    <div key={`s-${i}`} className="flex gap-4 p-4 glass rounded-2xl border-safe/10">
                                        <div className="h-10 w-10 shrink-0 glass rounded-xl flex items-center justify-center text-safe">
                                            <Check className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <div className="text-sm font-black leading-tight text-safe/80">Safety Tip</div>
                                            <p className="text-xs text-muted-foreground mt-1">{cond}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* API Intelligence (Merged) */}
                        {result.api_signals && result.api_signals.length > 0 && (
                            <div className="animate-slide-up stagger-4 glass-card bg-primary/5 border-primary/20">
                                <h4 className="text-lg font-black mb-6 flex items-center gap-2">
                                    <Sparkles className="w-6 h-6 text-primary" /> API Signal Fusion
                                </h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {result.api_signals.map((sig: any, i: number) => (
                                        <div key={i} className="glass p-4 rounded-2xl border-white/20 hover:border-primary/40 transition-all group flex items-start gap-4">
                                            <div className="text-2xl group-hover:scale-125 transition-transform">{sig.icon}</div>
                                            <div className="min-w-0">
                                                <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{sig.api}</div>
                                                <div className={`text-sm font-black ${sig.flagged ? 'text-danger' : 'text-safe'}`}>{sig.verdict}</div>
                                                <div className="text-[10px] truncate opacity-60 mt-0.5">{sig.detail}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                    </div>
                </div>
            </main>
        </div>
    );
}
