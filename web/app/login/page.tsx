"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { login, register } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("demo1234");
  const [name, setName] = useState("Demo User");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password, name);
      router.push("/board");
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="text-2xl font-bold mb-6">{mode === "login" ? "Вход" : "Регистрация"}</h1>
      <form onSubmit={submit} className="space-y-4">
        {mode === "register" && (
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Имя"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
          />
        )}
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" className="w-full bg-emerald-600 py-2 rounded-lg font-medium">
          {mode === "login" ? "Войти" : "Зарегистрироваться"}
        </button>
      </form>
      <button
        type="button"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
        className="mt-4 text-sm text-slate-400 hover:text-white"
      >
        {mode === "login" ? "Создать аккаунт" : "Уже есть аккаунт"}
      </button>
    </div>
  );
}
