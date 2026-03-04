"use client"

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheck, Zap } from 'lucide-react';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { cn } from '@/lib/utils';

export function Navbar() {
    const pathname = usePathname();

    const navItems = [
        { name: 'Analyze', href: '/analyze' },
        { name: 'Results', href: '/results' },
        { name: 'Comparison', href: '/analyze/compare' },
        { name: 'Live Demo', href: '/demo' },
    ];

    return (
        <header className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
            <nav className="glass max-w-5xl w-full h-16 rounded-3xl flex items-center justify-between px-6 transition-all duration-300 hover:shadow-primary/20">
                {/* Logo Section */}
                <Link href="/" className="group flex items-center gap-2 font-display text-xl font-bold transition-all duration-300 active:scale-95">
                    <div className="relative">
                        <ShieldCheck className="h-7 w-7 text-primary animate-float" />
                        <Zap className="h-3 w-3 text-accent absolute -top-1 -right-1 animate-pulse" />
                    </div>
                    <span className="hidden sm:inline-block tracking-tight">
                        Fraud<span className="text-primary italic">Guard</span>
                    </span>
                </Link>

                {/* Navigation Links */}
                <div className="hidden md:flex items-center gap-1 bg-muted/40 p-1.5 rounded-2xl">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "relative px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-500 overflow-hidden group",
                                pathname === item.href
                                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                                    : "text-muted-foreground hover:text-foreground hover:bg-white/10"
                            )}
                        >
                            <span className="relative z-10">{item.name}</span>
                            {pathname !== item.href && (
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                            )}
                        </Link>
                    ))}
                </div>

                {/* Actions Area */}
                <div className="flex items-center gap-4">
                    <div className="h-8 w-[1px] bg-border/50 hidden sm:block" />
                    <ThemeToggle />
                    <Link
                        href="/analyze"
                        className="hidden sm:flex items-center gap-2 bg-foreground text-background px-4 py-2 rounded-xl text-sm font-bold hover:opacity-90 active:scale-95 transition-all"
                    >
                        Get Started
                    </Link>
                </div>
            </nav>
        </header>
    );
}
