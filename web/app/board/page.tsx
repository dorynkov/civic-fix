"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchBoard, type Issue } from "@/lib/api";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

const STATUS_LABEL: Record<string, string> = {
  registered: "Зарегистрировано",
  linked: "Привязано",
  in_moderation: "На модерации",
  in_progress: "В работе",
  claimed_fixed: "З заявлено устранение",
  verifying: "Проверка",
  closed: "Закрыто",
  rejected: "Отклонено",
  reopened: "Переоткрыто",
};

export default function BoardPage() {
  const [items, setItems] = useState<Issue[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchBoard()
      .then((d) => setItems(d.items))
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Доска жалоб — Москва</h1>
        <Link
          href="/issues/new"
          className="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-lg text-sm font-medium"
        >
          + Сообщить о проблеме
        </Link>
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <MapView issues={items} />
      <ul className="space-y-3">
        {items.map((issue) => (
          <li key={issue.id} className="border border-slate-800 rounded-xl p-4 bg-slate-900/50">
            <Link href={`/issues/${issue.id}`} className="block hover:text-emerald-400">
              <div className="flex justify-between gap-2">
                <span className="font-medium">#{issue.id} {issue.title}</span>
                <span className="text-xs text-slate-400 uppercase">{issue.mode}</span>
              </div>
              <p className="text-sm text-slate-400 mt-1">{issue.address_text || "Москва"}</p>
              <div className="flex flex-wrap gap-3 mt-2 text-xs text-slate-300">
                {issue.public_status && (
                  <span className="bg-slate-800 px-2 py-1 rounded">
                    {STATUS_LABEL[issue.public_status] || issue.public_status}
                  </span>
                )}
                {issue.mode === "collective" && issue.signature_goal != null && (
                  <span>
                    Подписи: {issue.signature_count}/{issue.signature_goal}
                  </span>
                )}
                {issue.external_case_number_masked && (
                  <span>№ {issue.external_case_number_masked}</span>
                )}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
