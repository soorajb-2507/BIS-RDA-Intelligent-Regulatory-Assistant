import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'BIS AI Regulatory Assistant | Bureau of Indian Standards',
  description: 'Evidence-backed regulatory question answering, standards retrieval, and certification guidance.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
