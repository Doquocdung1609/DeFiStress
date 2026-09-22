import { Dashboard } from "../../components/Dashboard";

export default async function ResultPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;
  return <Dashboard section="results" runId={runId} />;
}

