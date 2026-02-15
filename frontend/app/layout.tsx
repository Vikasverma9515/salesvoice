import type { Metadata } from "next";
import { DM_Sans, Libre_Baskerville } from "next/font/google";
import "../globals.css";

const dmSans = DM_Sans({ subsets: ["latin"], variable: "--font-dm-sans" });
const libreBaskerville = Libre_Baskerville({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-libre"
});

export const metadata: Metadata = {
  title: "Salesvoice | AI Sales Agent",
  description: "Real-time AI Voice Sales Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${dmSans.variable} ${libreBaskerville.variable} font-sans antialiased bg-black text-white`}>
        {children}
      </body>
    </html>
  );
}
