"use client";
import { useState } from "react";
import { KeyRound, ShieldCheck, ShieldX, Download } from "lucide-react";
import { canUseNoble, generateKeyPair, signText } from "@/lib/crypto/webCrypto";
import { loadKey, saveKey } from "@/lib/crypto/keyStorage";
import { creatorApi } from "../services/creatorApi";

export default function KeyManagement({ creatorId, keys, onChanged }) {
    const [busy, setBusy] = useState(false);
    const [status, setStatus] = useState(null); // {ok, text}
    const [localKey, setLocalKey] = useState(null);

    async function generateAndRegister() {
        setBusy(true);
        setStatus(null);
        try {
        if (!canUseNoble()) throw new Error("Crypto unavailable in this browser");
            const kp = generateKeyPair();
            const registered = await creatorApi.registerKey(creatorId, {
                public_key: kp.publicKeyB64,
                algorithm: "ed25519",
                label: `browser-${new Date().toISOString().slice(0, 10)}`,
            });
            const record = { ...kp, backendKeyId: registered.key_id, createdAt: Date.now() };
            await saveKey(creatorId, record);
            setLocalKey(record);
            setStatus({ ok: true, text: `Key ${registered.key_id.slice(0, 12)}… registered` });
            onChanged?.();
        } catch (e) {
            setStatus({ ok: false, text: e.detail ?? e.message ?? "Failed" });
        } finally {
            setBusy(false);
        }
    }

  async function runSignatureTest() {
    setBusy(true);
    setStatus(null);
    try {
        const stored = localKey ?? (await loadKey(creatorId));
        if (!stored) throw new Error("No local private key. Generate one first.");
        const payload = `provenance-m2-test:${creatorId}:${Date.now()}`;
        const signature = await signText(stored.privateKeyHex, payload);
        const result = await creatorApi.verifySignature(creatorId, {
            payload, signature, key_id: stored.backendKeyId,
        });
        setStatus({
            ok: result.valid,
            text: result.valid
            ? "Signature verified by backend"
            : `Rejected: ${result.reason}`,
        });
    } catch (e) {
        setStatus({ ok: false, text: e.detail ?? e.message ?? "Failed" });
    } finally {
        setBusy(false);
    }
  }

    async function exportBackup() {
        const stored = localKey ?? (await loadKey(creatorId));
        if (!stored) return;
            const blob = new Blob([JSON.stringify(stored, null, 2)], {
            type: "application/json",
        });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `provenance-key-${creatorId}.json`;
        a.click();
        URL.revokeObjectURL(a.href);
    }

    return (
        <section className="space-y-4 rounded-xl border p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
            <KeyRound size={18} /> Signing keys
        </h2>

        <p className="text-sm text-slate-600">
            Your private key is generated and stored only in this browser
            (IndexedDB). It is not a secure vault against malware — export a
            backup and keep it offline.
        </p>

        <div className="flex flex-wrap gap-2">
            <button onClick={generateAndRegister} disabled={busy}
                className="rounded-lg bg-slate-900 px-3 py-2 text-white disabled:opacity-50">
                Generate &amp; register key
            </button>
            <button onClick={runSignatureTest} disabled={busy}
                className="rounded-lg border px-3 py-2 disabled:opacity-50">
                Test signature
            </button>
            <button onClick={exportBackup} disabled={busy}
                className="flex items-center gap-1 rounded-lg border px-3 py-2 disabled:opacity-50">
            <Download size={16} /> Export backup
            </button>
        </div>

        {status && (
            <p className={`flex items-center gap-2 text-sm ${
            status.ok ? "text-green-700" : "text-red-600"}`}>
            {status.ok ? <ShieldCheck size={16} /> : <ShieldX size={16} />}
            {status.text}
            </p>
        )}

        <table className="w-full text-sm">
            <thead className="text-left text-slate-500">
            <tr><th>Key ID</th><th>Label</th><th>Status</th><th /></tr>
            </thead>
            <tbody>
            {keys.map((k) => (
                <tr key={k.id} className="border-t">
                <td className="py-2 font-mono text-xs">{k.key_id.slice(0, 16)}…</td>
                <td>{k.label ?? "—"}</td>
                <td>{k.status}</td>
                <td className="text-right">
                    {k.status === "active" && (
                    <button
                        onClick={async () => {
                        await creatorApi.revokeKey(creatorId, k.key_id);
                        onChanged?.();
                        }}
                        className="text-red-600 hover:underline"
                    >Revoke</button>
                    )}
                </td>
                </tr>
            ))}
            {keys.length === 0 && (
                <tr><td colSpan={4} className="py-3 text-slate-500">No keys yet.</td></tr>
            )}
            </tbody>
        </table>
        </section>
    );
}