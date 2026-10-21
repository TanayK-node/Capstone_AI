import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "PaperLens",
  description: "Grounded, reproducibility-aware research paper extraction",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <Providers>
          <nav className="border-b border-zinc-200 px-6 py-3 dark:border-zinc-800">
            <Link href="/" className="font-semibold tracking-tight">
              PaperLens
            </Link>
          </nav>
          {children}
        </Providers>
      </body>
    </html>
  );
}
