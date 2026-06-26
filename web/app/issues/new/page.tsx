"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createIssue } from "@/lib/api";

export default function NewIssuePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [mode, setMode] = useState<"personal" | "collective">("personal");
  const [lat, setLat] = useState(55.751);
  const [lon, setLon] = useState(37.618);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const issue = await createIssue({
        title,
        description,
        mode,
        latitude: lat,
        longitude: lon,
        address_text: "Москва",
        category: "pothole_street",
        signature_goal: 10,
      });
      router.push(`/issues/${issue.id}`);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">Сообщить о проблеме</h1>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">Тип</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as "personal" | "collective")}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
          >
            <option value="personal">Персональная</option>
            <option value="collective">Сразу коллективная</option>
          </select>
        </div>
        <div>
          <label className="block text-sm mb-1">Заголовок</label>
          <input
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
            placeholder="Яма на тротуаре"
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 min-h-[80px]"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm mb-1">Широта</label>
            <input
              type="number"
              step="0.0001"
              value={lat}
              onChange={(e) => setLat(parseFloat(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Долгота</label>
            <input
              type="number"
              step="0.0001"
              value={lon}
              onChange={(e) => setLon(parseFloat(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2"
            />
          </div>
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 py-2 rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? "…" : "Создать"}
        </button>
      </form>
      <p className="text-xs text-slate-500 mt-4">
        Demo: demo@example.com / demo1234 —{" "}
        <a href="/login" className="text-emerald-400">
          войти
        </a>
      </p>
    </div>
  );
}
