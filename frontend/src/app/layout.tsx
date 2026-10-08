import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JobPulse — Job Market Intelligence",
  description:
    "Personal job market intelligence dashboard. Analyze skills demand, trends, and gaps.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-[family-name:var(--font-inter)]">
        <Sidebar />
        <main className="flex-1 ml-64 min-h-screen">
          <div className="p-8">{children}</div>
        </main>
      </body>
    </html>
  );
}
