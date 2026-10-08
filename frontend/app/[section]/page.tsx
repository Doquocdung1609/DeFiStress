import { Dashboard } from "../components/Dashboard";

const sections = new Set([
  "overview",
  "positions",
  "liquidity",
  "scenarios",
  "simulator",
  "contagion",
  "compare",
  "validation",
  "provenance",
]);

export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  return <Dashboard section={sections.has(section) ? section : "overview"} />;
}
