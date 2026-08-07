import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Nava AI Outbound Intelligence Platform",
  description: "AI-assisted B2B prospect intelligence and outbound workflow",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex">
          <Nav />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
