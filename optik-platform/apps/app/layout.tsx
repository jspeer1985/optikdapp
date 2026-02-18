import './globals.css';
import Providers from './providers';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import OptikGPT from './components/OptikGPT/OptikGPT';
import { Outfit } from 'next/font/google';

const outfit = Outfit({
  subsets: ['latin'],
  display: 'swap',
});

export const metadata = {
  title: 'Optik Platform',
  description: 'Web3 infrastructure for building and scaling decentralized applications.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={outfit.className}>
      <body className="app-body">
        <Providers>
          <Navbar />
          <main className="main-content">{children}</main>
          <Footer />
          <OptikGPT />
        </Providers>
      </body>
    </html>
  );
}
