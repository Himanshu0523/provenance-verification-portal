"use client";

import { useMemo } from "react";
import Image from "next/image";

export default function PublishPreview({ file, onPublish, onClear, busy, error }) {
    const url = useMemo(() => {
        if (!file) return null;
        const u = URL.createObjectURL(file);
        return u;
    }, [file]);

    if (!file) return null;

    return (
        <div className="space-y-3 rounded-xl border p-4">
        {url && (
            <div className="relative max-h-64 w-full overflow-hidden rounded-lg">
                <Image 
                    src={url} 
                    alt="preview"
                    width={500}
                    height={256}
                    unoptimized
                    className="max-h-64 w-full object-contain" 
                />
            </div>
        )}
        <dl className="grid grid-cols-2 gap-1 text-sm">
            <dt className="text-slate-500">Name</dt><dd>{file.name}</dd>
            <dt className="text-slate-500">Type</dt><dd>{file.type || "—"}</dd>
            <dt className="text-slate-500">Size</dt>
            <dd>{Math.round(file.size / 1024)} KB</dd>
        </dl>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-2">
            <button onClick={onPublish} disabled={busy}
                className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50">
                {busy ? "Publishing…" : "Publish & sign"}
            </button>
            <button onClick={onClear} disabled={busy}
                className="rounded-lg border px-4 py-2 disabled:opacity-50">
                Clear
            </button>
        </div>
        </div>
    );
}