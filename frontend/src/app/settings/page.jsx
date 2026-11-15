"use client";
import { useState } from "react";
import { useCreator } from "@/features/creators/hooks/useCreator";
import CreatorRegistration from "@/features/creators/components/CreatorRegistration";
import KeyManagement from "@/features/creators/components/KeyManagement";

export default function SettingsPage() {
    const { creator, keys, loading, refresh } = useCreator();
    const [registered, setRegistered] = useState(null);

    const activeCreator = creator ?? registered;

    if (loading && !activeCreator) return <p className="p-6">Loading…</p>;

    return (
        <main className="mx-auto max-w-3xl space-y-6 p-6">
        <h1 className="text-2xl font-bold">Creator identity &amp; keys</h1>

        {!activeCreator ? (
            <CreatorRegistration onRegistered={setRegistered} />
        ) : (
            <>
            <section className="rounded-xl border p-5 text-sm">
                <div><span className="text-slate-500">Creator ID: </span>
                <code className="font-mono">{activeCreator.id}</code></div>
                <div><span className="text-slate-500">Name: </span>
                {activeCreator.display_name}</div>
            </section>
            <KeyManagement
                creatorId={activeCreator.id}
                keys={keys}
                onChanged={() => refresh(activeCreator.id)}
            />
            </>
        )}
        </main>
    );
}