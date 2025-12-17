import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Phase III - AI Task Manager",
  description: "Conversational task management powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* 
          ChatKit integration will be added here when T032 is completed.
          For now, this provides a basic layout structure.
          
          After cloning ChatKit starter (T032), integrate ChatKit provider:
          <ChatkitProvider config={{domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY}}>
            {children}
          </ChatkitProvider>
        */}
        {children}
      </body>
    </html>
  );
}
