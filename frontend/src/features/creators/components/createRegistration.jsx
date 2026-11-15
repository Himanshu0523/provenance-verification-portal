"use client";
import { useState } from "react";
import { UserPlus } from "lucide-react";
import { useCreator } from "../hooks/useCreator";

export default function CreatorRegistration({ onRegistered }) {
    const { register, loading, error } = useCreator();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [localError, setLocalError] = useState(null);

    async function submit(e) {
        e.preventDefault();
        setLocalError(null);
        try {
        const c = await register(name.trim(), email.trim());
        onRegistered?.(c);
        } catch (err) {
        setLocalError(err.detail ?? "Registration failed");
        }
    }

  return (
        <form onSubmit={submit} className="space-y-3 rounded-xl border p-5">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
                <UserPlus size={18} /> Register creator
            </h2>

            <input
                required minLength={1} maxLength={255} value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Display name"
                className="w-full rounded-lg border px-3 py-2"
            />
            <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="Email (optional)"
                className="w-full rounded-lg border px-3 py-2"
            />

            {(localError || error) && (
                <p className="text-sm text-red-600">{localError || error}</p>
            )}

            <button
                type="submit" disabled={loading || !name.trim()}
                className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
            >
                {loading ? "Registering…" : "Register"}
            </button>
        </form>
  );
}