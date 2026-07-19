import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Target, Loader2, AlertCircle, Sparkles } from "lucide-react";
import { listInitiatives, initiativeStatus, type Initiative } from "@/lib/api";

/**
 * Initiatives tab — lists goals/projects the brain tracks, and on demand
 * synthesizes a coach-style status (from the notes & meetings linked to each).
 */
export function InitiativesView() {
    const [initiatives, setInitiatives] = useState<Initiative[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [openSlug, setOpenSlug] = useState<string | null>(null);
    const [status, setStatus] = useState<string>("");
    const [statusLoading, setStatusLoading] = useState(false);

    useEffect(() => {
        (async () => {
            setIsLoading(true);
            setError(null);
            try {
                setInitiatives(await listInitiatives());
            } catch (e) {
                setError(e instanceof Error ? e.message : String(e));
            } finally {
                setIsLoading(false);
            }
        })();
    }, []);

    const openStatus = async (it: Initiative) => {
        if (openSlug === it.slug) { setOpenSlug(null); return; }
        setOpenSlug(it.slug);
        setStatus("");
        setStatusLoading(true);
        try {
            const res = await initiativeStatus(it.slug);
            setStatus(res.status);
        } catch (e) {
            setStatus(`Couldn't get a status: ${e instanceof Error ? e.message : String(e)}`);
        } finally {
            setStatusLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Initiatives</h2>
                <p className="text-muted-foreground">
                    Goals your brain tracks — say <span className="font-mono">"start an initiative…"</span> in a note.
                    Notes and meetings link to them automatically.
                </p>
            </div>

            {isLoading ? (
                <div className="flex items-center justify-center h-48">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
            ) : error ? (
                <div className="flex flex-col items-center justify-center h-48 gap-2 text-destructive">
                    <AlertCircle className="h-8 w-8" />
                    <p className="text-sm">{error}</p>
                </div>
            ) : initiatives.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-muted-foreground">
                    <p className="text-sm">No initiatives yet — capture a note saying "start an initiative to…".</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {initiatives.map((it) => (
                        <Card key={it.slug}>
                            <CardHeader>
                                <div className="flex items-start justify-between gap-4">
                                    <div className="space-y-1">
                                        <CardTitle className="flex items-center gap-2">
                                            <Target className="h-5 w-5 text-primary" />
                                            {it.title}
                                        </CardTitle>
                                        <CardDescription>
                                            {it.linked} linked capture{it.linked === 1 ? "" : "s"} · {it.status}
                                        </CardDescription>
                                    </div>
                                    <Button variant="outline" size="sm" onClick={() => openStatus(it)}>
                                        <Sparkles className="h-4 w-4 mr-1" />
                                        {openSlug === it.slug ? "Hide" : "Status"}
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {it.goals.length > 0 && (
                                    <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
                                        {it.goals.map((g, i) => <li key={i}>{g}</li>)}
                                    </ul>
                                )}
                                {openSlug === it.slug && (
                                    <div className="rounded-lg border bg-muted/30 p-4">
                                        {statusLoading ? (
                                            <div className="flex items-center gap-2 text-muted-foreground">
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                <span className="text-sm">Reviewing your progress…</span>
                                            </div>
                                        ) : (
                                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{status}</p>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
