import { TerraDashboard } from "../../components/terra/TerraDashboard";

const sections = new Set([
  "overview",
  "historical-data",
  "historical-fit",
  "early-warning",
  "stress-test",
  "model-comparison",
  "mechanism-check",
  "data-sources",
  "wallet-dynamics",
  "model-lab",
  "replay",
  "benchmark",
  "ablation",
  "counterfactual",
  "provenance",
]);

export default async function TerraSectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  return <TerraDashboard section={sections.has(section) ? section : "overview"} />;
}
