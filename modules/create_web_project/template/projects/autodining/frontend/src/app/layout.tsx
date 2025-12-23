import type React from "react";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ClientBody from "./ClientBody";
import { SeedProvider } from "@/context/SeedContext";
import { Suspense } from "react";
import { SeedRedirect } from "@/components/layout/SeedRedirect";
import { DynamicDebug } from "@/components/debug/DynamicDebug";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AutoDining | Easy Restaurant Reservations & Dining Bookings",
  description: "Book your favorite restaurants effortlessly with AutoDining. Discover top dining spots, reserve tables instantly, and enjoy a seamless restaurant booking experience.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <body className="antialiased" suppressHydrationWarning>
        <ClientBody>
          <Suspense fallback={<div>Loading...</div>}>
            <SeedProvider>
              <Suspense fallback={null}>
                <SeedRedirect />
              </Suspense>
              {children}
              <DynamicDebug />
            </SeedProvider>
          </Suspense>
        </ClientBody>
      </body>
    </html>
  );
}
