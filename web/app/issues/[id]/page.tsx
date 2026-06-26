"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  fetchIssue,
  fetchPetitionByIssue,
  linkCase,
  mockSubmit,
  signPetition,
  upgradeCollective,
  type Issue,
} from "@/lib/api";

export default function IssuePage() {
  const params = useParams();
  const id = params.id as string;
  const [issue, setIssue] = useState<Issue | null>(null);
  const [petitionId, setPetitionId] = useState<number | null>(null);
  const [caseNumber, setCaseNumber] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function reload() {
    const i = await fetchIssue(id);
    setIssue(i);
    if (i.mode === "collective") {
      try {
        const p = await fetchPetitionByIssue(i.id);
        setPetitionId(p.id);
      } catch {
        setPetitionId(null);
      }
    }
  }

  useEffect(() => {
    reload().catch((e) => setError(String(e)));
  }, [id]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!issue) return <p className="text-slate-400">Загрузка…</p>;

  const goal = issue.signature_goal ?? 10;
  const count = issue.signature_count ?? 0;
  const canSubmit = issue.mode === "personal" || count >= goal;

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <p className="text-sm text-slate-400">#{issue.id} · {issue.mode}</p>
        <h1 className="text-2xl font-bold mt-1">{issue.title}</h1>
        <p className="text-slate-300 mt-2">{issue.description}</p>
        {issue.public_status && (
          <p className="mt-2 text-sm">
            Статус: <span className="text-emerald-400">{issue.public_status}</span>
            {issue.external_case_number_masked && ` · № ${issue.external_case_number_masked}`}
          </p>
        )}
      </div>

      {issue.mode === "collective" && (
        <div className="border border-slate-800 rounded-xl p-4">
          <p className="text-sm mb-2">
            Подписи: {count}/{goal}
          </p>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden mb-3">
            <div
              className="h-full bg-emerald-500"
              style={{ width: `${Math.min(100, (count / goal) * 100)}%` }}
            />
          </div>
          {petitionId && (
            <button
              onClick={async () => {
                await signPetition(petitionId);
                setMsg("Вы подписали");
                reload();
              }}
              className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm mr-2"
            >
              Подписать
            </button>
          )}
          <Link
            href={`/issues/${issue.id}/share`}
            className="inline-block bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded-lg text-sm"
          >
            Клич — поделиться
          </Link>
        </div>
      )}

      {issue.mode === "personal" && issue.status !== "submission_pending" && (
        <button
          onClick={async () => {
            await upgradeCollective(issue.id);
            setMsg("Сделано коллективным");
            reload();
          }}
          className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm"
        >
          Сделать коллективным
        </button>
      )}

      {canSubmit && (
        <div className="border border-slate-800 rounded-xl p-4 space-y-3">
          <h2 className="font-medium">Подача в органы (P0 demo)</h2>
          <button
            onClick={async () => {
              const r = await mockSubmit(issue.id);
              window.open(r.redirect_url, "_blank");
              setMsg("Откройте «Наш город», подайте заявку, затем введите № ниже");
              reload();
            }}
            className="bg-blue-700 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm"
          >
            Подать (mock → gorod.mos.ru)
          </button>
          <div className="flex gap-2">
            <input
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              placeholder="№ заявки из ЛК"
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
            />
            <button
              onClick={async () => {
                await linkCase(issue.id, caseNumber);
                setMsg("Номер привязан — смотрите доску");
                reload();
              }}
              className="bg-emerald-700 px-4 py-2 rounded-lg text-sm"
            >
              Link
            </button>
          </div>
        </div>
      )}

      {msg && <p className="text-emerald-400 text-sm">{msg}</p>}
      <Link href="/board" className="text-sm text-slate-400 hover:text-white">
        ← На доску
      </Link>
    </div>
  );
}
