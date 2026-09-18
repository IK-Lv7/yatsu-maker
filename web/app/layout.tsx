import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import Header from "./components/Header";
import "./globals.css";

const notoSansJP = Noto_Sans_JP({
  variable: "--font-noto-sans-jp",
  subsets: ["latin"],
  weight: ["400", "500", "700", "900"],
});

export const metadata: Metadata = {
  title: "AI〜な奴メーカー",
  description:
    "「〜奴」形式のタイトルを学習したAIが、毎日新しいタイトルを生成するファンメイドサイト",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ja" className={`${notoSansJP.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-orange-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
        <Header />
        {children}
      </body>
    </html>
  );
}
