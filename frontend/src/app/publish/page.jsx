"use client";
import { useState } from "react";
import { useCreator } from "@/features/creators/hooks/useCreator";
import { usePublish } from "@/features/publishing/hooks/usePublish";
import PublishUploader from "@/features/publishing/components/PublishUploader";
import PublishPreview from "@/features/publishing/components/PublishPreview";
import PublishResult from "@/features/publishing/components/PublishResult";

export default function PublishPage() {
    const { creator, loading } = useCreator();
    const { publish, stage, error, result, reset } = usePublish(creator?.id);
    const [file, setFile] = useState(null);

    if (loading) return <p className="p-6">Loading creator…</p>;
    if (!creator)
        return <p className="p-6">Register a creator first at <a className="underline" href="/settings">Settings</a>.</p>;

    return (
        <main className="mx-auto max-w-3xl space-y-4 p-6">
        <h1 className="text-2xl font-bold">Publish Studio</h1>

        {!result && (
            <>
            <PublishUploader onFile={setFile}
                disabled={!["idle", "error"].includes(stage)} />
            {file && (
                <PublishPreview
                file={file}
                busy={stage === "hashing" || stage === "signing" || stage === "uploading"}
                error={stage === "error" ? error : null}
                onPublish={() => publish(file)}
                onClear={() => setFile(null)}
                />
            )}
            </>
        )}

        {result && (
            <PublishResult
            result={result}
            onReset={() => { setFile(null); reset(); }}
            />
        )}
        </main>
    );
}