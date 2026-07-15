import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: {
    default: "NiralayOS — Luxury Resort & Restaurant Management",
    template: "%s | NiralayOS",
  },
  description:
    "NiralayOS is a premium hospitality operating system for luxury resorts and restaurants. Manage reservations, rooms, billing, inventory, and finance from a single unified platform.",
  keywords: [
    "hotel management",
    "resort PMS",
    "restaurant billing",
    "hospitality software",
    "NiralayOS",
  ],
  authors: [{ name: "Niralay Software" }],
  robots: "noindex, nofollow",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background font-sans antialiased">{children}</body>
    </html>
  );
}
