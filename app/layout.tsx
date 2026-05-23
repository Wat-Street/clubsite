import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import { ThemeProvider } from "@/components/layout/themeProvider";
import FixedHeader from "@/components/clubsite/FixedHeader";

const proxima = localFont({
  src: [
    {
      path: "./fonts/proxima_nova_regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/proxima_nova_semibold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "./fonts/proxima_nova_bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
});

export const metadata: Metadata = {
  title: "Wat Street",
  description: "The University of Waterloo's quantitative finance design team.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="!scroll-smooth">
      <body className={`${proxima.className}`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          forcedTheme="dark"
          disableTransitionOnChange
        >
          <FixedHeader />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
