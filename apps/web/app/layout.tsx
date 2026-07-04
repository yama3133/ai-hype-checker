import type { Metadata } from "next";
import { LINE_Seed_JP, Geist_Mono } from "next/font/google";
import "./globals.css";
import { I18nProvider } from "@/lib/i18n-context";

const lineSeed = LINE_Seed_JP({
  variable: "--font-line-seed",
  weight: ["400", "700"],
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI驚き屋発見器",
  description: "X（旧Twitter）のAI関連投稿の誇張・扇動表現を分析し「驚き屋度」を判定します",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ja"
      className={`${lineSeed.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans font-bold">
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
