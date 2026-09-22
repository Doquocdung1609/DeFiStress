import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DeFiStress Lab",
  description: "Aave V3 and Uniswap V3 contagion stress research dashboard",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

