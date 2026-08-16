import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Stats from '../components/Stats';
import Features from '../components/Features';
import AICopilot from '../components/AICopilot';
import CTA from '../components/CTA';
import Footer from '../components/Footer';
export default function LandingPage() {
    return (<div className="min-h-screen">
      <Navbar />
      <Hero />
      <Stats />
      <Features />
      <AICopilot />
      <CTA />
      <Footer />
    </div>);
}
