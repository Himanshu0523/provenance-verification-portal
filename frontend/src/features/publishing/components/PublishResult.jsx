"use client";

import Link from "next/link";
import Image from "next/image";
import { CheckCircle2 } from "lucide-react";

export default function PublishResult({ result, onReset }) {
    if (!result) return null;
    return (
        <div className="space-y-3 rounded-xl border p-4">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-green-700">
            <CheckCircle2 size={18} /> Published
        </h2>
        <dl className="space-y-1 text-sm">
            <div>
            <dt className="inline text-slate-500">Asset ID: </dt>
            <dd className="inline font-mono">{result.asset_id}</dd>
            </div>
            <div>
            <dt className="inline text-slate-500">SHA-256: </dt>
            <dd className="inline break-all font-mono text-xs">{result.sha256}</dd>
            </div>
            <div>
            <dt className="inline text-slate-500">pHash: </dt>
            <dd className="inline font-mono">{result.perceptual_hash ?? "—"}</dd>
            </div>
        </dl>
        {result.preview_url && (
            <div className="relative max-h-48 w-full overflow-hidden rounded-lg border">
                <Image
                    src={result.preview_url}
                    alt="published"
                    width={400}
                    height={192}
                    unoptimized
                    className="max-h-48 w-full object-contain"
                />
            </div>
        )}
        <div className="flex gap-2">
            <Link
            href={result.verification_url}
            className="rounded-lg bg-slate-900 px-4 py-2 text-white"
            >
            Open verification page
            </Link>
            <button
            onClick={onReset}
            className="rounded-lg border px-4 py-2"
            >
            Publish another
            </button>
        </div>
        </div>
    );
}