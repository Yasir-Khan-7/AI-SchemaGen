import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { Copy, Download, Loader2, UploadCloud } from "lucide-react";
import { generateSchema, GenerateResponse } from "./lib/api";
import { cn } from "./utils";

type Status = "idle" | "loading" | "success" | "error";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const hasResult = useMemo(() => Boolean(result?.xml), [result]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setResult(null);
    setError(null);
    setCopied(false);
    const selected = event.target.files?.[0];
    if (selected && selected.type !== "application/pdf") {
      setError("Please choose a PDF file.");
      setFile(null);
      return;
    }
    setFile(selected ?? null);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      setError("Upload a PDF first.");
      return;
    }

    setStatus("loading");
    setError(null);
    setCopied(false);

    try {
      const response = await generateSchema(file);
      setResult(response);
      setStatus("success");
    } catch (err) {
      setStatus("error");
      setResult(null);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  const handleCopy = async () => {
    if (!result?.xml) return;
    await navigator.clipboard.writeText(result.xml);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  const handleDownload = () => {
    if (!result?.xml || !result.filename) return;
    const blob = new Blob([result.xml], { type: "application/xml" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = result.filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-slate-950 to-zinc-900 text-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <header className="mb-10 space-y-3 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-amber-300">AI SchemaGen</p>
          <h1 className="text-4xl font-semibold sm:text-5xl">
            Convert PDFs to clean{" "}
            <span className="bg-gradient-to-r from-amber-400 via-orange-400 to-rose-400 bg-clip-text text-transparent">
              XML schemas
            </span>
          </h1>
          <p className="mx-auto max-w-3xl text-base text-slate-300">
            Turn your PDFs into structured XML in one click—clear, fast, and ready to use.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
          <div className="rounded-2xl border border-slate-800/70 bg-slate-900/60 p-6 shadow-2xl shadow-cyan-500/5 backdrop-blur">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-amber-300">Upload</p>
                <h2 className="text-xl font-semibold">PDF Source</h2>
                <p className="text-sm text-slate-400">Upload a PDF and generate its XML instantly.</p>
              </div>
              <div className="rounded-full bg-amber-500/10 px-4 py-2 text-xs font-medium text-amber-200">Secure</div>
            </div>

            <label
              className={cn(
                "group relative block cursor-pointer rounded-xl border-2 border-dashed border-slate-700 bg-slate-900/40 p-6 transition hover:border-amber-400/80 hover:bg-slate-900/70",
                status === "loading" ? "pointer-events-none opacity-70" : "",
              )}
            >
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
                aria-label="Upload PDF"
              />
              <div className="flex flex-col items-center justify-center space-y-3 text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/10 text-cyan-300">
                  <UploadCloud className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-lg font-medium">
                    {file ? `Selected: ${file.name}` : "Drop your PDF here or click to browse"}
                  </p>
                  <p className="text-sm text-slate-400">Max 20MB • PDF only</p>
                </div>
              </div>
            </label>

            <button
              type="submit"
              className={cn(
                "mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-amber-500/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 focus:ring-offset-slate-950",
                status === "loading" ? "cursor-wait opacity-80" : "",
              )}
              disabled={status === "loading"}
            >
              {status === "loading" ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Converting...
                </>
              ) : (
                "Generate XML"
              )}
            </button>

            {error && (
              <div className="mt-4 rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                {error}
              </div>
            )}
          </div>

          <div className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-900/60 shadow-2xl shadow-blue-500/5 backdrop-blur">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 via-transparent to-rose-500/10" />
            <div className="relative flex items-center justify-between border-b border-slate-800/70 px-5 py-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-amber-200">Result</p>
                <h2 className="text-lg font-semibold">XML Output</h2>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleCopy}
                  disabled={!hasResult}
                  className={cn(
                    "inline-flex items-center gap-2 rounded-lg border border-slate-700/80 bg-slate-900/60 px-3 py-2 text-xs font-medium text-slate-100 transition hover:border-amber-400/60 hover:text-white",
                    !hasResult && "cursor-not-allowed opacity-60",
                  )}
                >
                  <Copy className="h-4 w-4" />
                  {copied ? "Copied" : "Copy"}
                </button>
                <button
                  type="button"
                  onClick={handleDownload}
                  disabled={!hasResult}
                  className={cn(
                    "inline-flex items-center gap-2 rounded-lg border border-amber-500/60 bg-amber-500/10 px-3 py-2 text-xs font-medium text-amber-100 transition hover:bg-amber-500/20",
                    !hasResult && "cursor-not-allowed opacity-60",
                  )}
                >
                  <Download className="h-4 w-4" />
                  Download
                </button>
              </div>
            </div>

            <div className="relative max-h-[560px] overflow-y-auto p-5 text-sm leading-relaxed text-slate-100">
              {!hasResult && status !== "loading" && (
                <div className="rounded-lg border border-slate-800/80 bg-slate-950/60 px-4 py-8 text-center text-slate-400">
                  Upload a PDF and tap Generate to see XML here.
                </div>
              )}

              {status === "loading" && (
                <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-slate-800/80 bg-slate-950/60 px-4 py-8 text-slate-300">
                  <Loader2 className="h-6 w-6 animate-spin text-amber-300" />
                  <p>Calling the model and building your XML…</p>
                </div>
              )}

              {hasResult && (
                <pre className="whitespace-pre-wrap rounded-lg border border-slate-800/80 bg-slate-950/70 p-4 font-mono text-xs text-slate-100">
                  {result?.xml}
                </pre>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;

