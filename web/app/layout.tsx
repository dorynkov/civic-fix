import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Civic Fix — коллективные обращения",
  description: "Жалобы на городские проблемы, Москва",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <header className="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
            <Link href="/board" className="font-semibold text-emerald-400">
              Civic Fix
            </Link>
            <nav className="flex gap-4 text-sm text-slate-300">
              <Link href="/board">Доска</Link>
              <Link href="/issues/new">Сообщить</Link>
              <Link href="/login">Вход</Link>
            </nav>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
