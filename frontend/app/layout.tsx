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
          <nav className="flex items-center gap-5 border-b border-zinc-200 px-6 py-3 text-sm dark:border-zinc-800">
            <Link href="/" className="text-base font-semibold tracking-tight">
              PaperLens
            </Link>
            <Link href="/" className="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100">
              Library
            </Link>
            <Link
              href="/compare"
              className="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
            >
              Compare
            </Link>
          </nav>
          {children}
        </Providers>
      </body>
    </html>
  );
}
