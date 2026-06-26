"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchIssue } from "@/lib/api";

export default function SharePage() {
  const params = useParams();
  const id = params.id as string;
  const [title, setTitle] = useState("");

  useEffect(() => {
    fetchIssue(id).then((i) => setTitle(i.title)).catch(() => {});
  }, [id]);

  const url = typeof window !== "undefined" ? `${window.location.origin}/issues/${id}` : "";

  return (
    <div className="max-w-md mx-auto text-center space-y-4">
      <h1 className="text-xl font-bold">Клич соседям</h1>
      <p className="text-slate-300">{title || `Жалоба #${id}`}</p>
      <p className="text-sm text-slate-400">
        Отправьте ссылку тем, кому тоже мешает эта проблема — пусть подпишут коллективное обращение.
      </p>
      <input
        readOnly
        value={url}
        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
      />
      <button
        onClick={() => navigator.clipboard.writeText(url)}
        className="bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded-lg text-sm"
      >
        Скопировать ссылку
      </button>
      <Link href={`/issues/${id}`} className="block text-sm text-slate-400">
        ← К карточке
      </Link>
    </div>
  );
}
