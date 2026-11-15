"use client";
import Link from "next/link";
import TrustBanner from "./TrustBanner";

function Row({ label, children }) {
  return (
    <div className="grid grid-cols-[140px_1fr] gap-2 text-sm">
      <dt className="text-slate-500">{label}</dt>
      <dd className="break-all font-mono text-xs">{children}</dd>
    </div>
  );
}

export default function VerificationResult({ result, onReset }) {
  if (!result) return null;
  return (
    <div className="space-y-4">
      <TrustBanner verdict={result.verdict} />

      <div className="rounded-xl border p-4">
        <Row label="Query SHA-256">{result.query_sha256}</Row>
        <Row label="Matches">{result.total_matches}</Row>
        <Row label="Audit ID">{result.audit_id ?? "—"}</Row>
      </div>

      {result.matches.map((m) => (
        <article key={m.asset_id} className="space-y-3 rounded-xl border p-4">
          <header className="flex items-center justify-between">
            <h3 className="font-semibold">
              {m.original_filename}{" "}
              <span className="text-sm font-normal text-slate-500">
                by {m.creator_display_name}
              </span>
            </h3>
            <span
              className={`rounded-full px-2 py-0.5 text-xs ${
                m.per_asset_verdict === "verified"
                  ? "bg-green-100 text-green-800"
                  : "bg-slate-100 text-slate-800"
              }`}
            >
              {m.per_asset_verdict}
            </span>
          </header>

          {m.preview_url && (
            <img
              src={m.preview_url}
              alt={m.original_filename}
              className="max-h-56 rounded-lg border object-contain"
            />
          )}

          <dl className="space-y-1">
            <Row label="Asset ID">{m.asset_id}</Row>
            <Row label="Creator ID">{m.creator_id}</Row>
            <Row label="Key ID">{m.key_id}</Row>
            <Row label="Key status">{m.key_status}</Row>
            <Row label="Signature">{m.signature_valid ? "valid" : "invalid"}</Row>
            <Row label="Manifest">{m.manifest_ok ? "intact" : "corrupt"}</Row>
            <Row label="Signed at">
              {new Date(m.signed_at).toLocaleString()}
            </Row>
            <Row label="Size">{m.file_size.toLocaleString()} bytes</Row>
          </dl>

          <Link
            href={`/lineage/${m.asset_id}`}
            className="inline-block rounded-lg border px-3 py-1.5 text-sm"
          >
            Open lineage
          </Link>
        </article>
      ))}

      <button
        onClick={onReset}
        className="rounded-lg border px-4 py-2 text-sm"
      >
        Verify another file
      </button>
    </div>
  );
}