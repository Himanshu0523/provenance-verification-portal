"use client";
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react";

const STYLES = {
  verified:          { bg: "bg-green-50 border-green-300 text-green-900",
                       Icon: CheckCircle2,
                       title: "Exact match, signature verified" },
  key_revoked:       { bg: "bg-amber-50 border-amber-300 text-amber-900",
                       Icon: AlertTriangle,
                       title: "Exact match, but the signing key has been revoked" },
  signature_invalid: { bg: "bg-red-50 border-red-300 text-red-900",
                       Icon: XCircle,
                       title: "Exact match, but the signature is invalid" },
  invalid_manifest:  { bg: "bg-red-50 border-red-300 text-red-900",
                       Icon: XCircle,
                       title: "Exact match, but the stored manifest is corrupt" },
  unknown:           { bg: "bg-slate-50 border-slate-300 text-slate-900",
                       Icon: HelpCircle,
                       title: "No exact match found" },
};

export default function TrustBanner({ verdict }) {
    const style = STYLES[verdict] ?? STYLES.unknown;
    const { Icon, bg, title } = style;
    return (
        <div className={`flex items-start gap-3 rounded-xl border p-4 ${bg}`}>
        <Icon className="mt-0.5 shrink-0" size={22} />
        <div>
            <p className="font-semibold">{title}</p>
            <p className="text-sm opacity-80">
            {verdict === "verified" &&
                "The uploaded file is byte-for-byte identical to a published asset, " +
                "and the signature was produced by the registered private key."}
            {verdict === "key_revoked" &&
                "The file exists and the signature is valid, but the signer has revoked " +
                "this key. The historical provenance is preserved; new trust should not be placed in it."}
            {verdict === "signature_invalid" &&
                "The file exists, but the signature on the stored record does not verify " +
                "against the registered public key. Treat the record as compromised."}
            {verdict === "invalid_manifest" &&
                "The file exists, but the stored provenance manifest is corrupt or " +
                "inconsistent with the asset's own metadata."}
            {verdict === "unknown" &&
                "No asset with this exact SHA-256 hash is registered. A modified or " +
                "unseen file will land here."}
            </p>
        </div>
        </div>
    );
}