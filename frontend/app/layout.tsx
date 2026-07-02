import type { Metadata } from "next";

import { Header } from "@/components/header";

import "./globals.css";

export const metadata: Metadata = {
  title: "번개중고 MVP",
  description: "한국어 기반 중고거래 웹서비스 MVP",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>
        <div className="shell">
          <Header />
          <main className="page-shell">{children}</main>
        </div>
      </body>
    </html>
  );
}
