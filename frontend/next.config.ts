import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Windows requires Developer Mode or elevated symlink privileges for the
  // standalone tracer. Docker/Linux still emits the deployment bundle.
  output: process.platform === "win32" ? undefined : "standalone",
  distDir: process.env.NEXT_DIST_DIR ?? ".next",
};

export default nextConfig;
