import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { DetectionPage } from './pages/DetectionPage';
import { HistoryPage } from './pages/HistoryPage';
import { ReportsPage } from './pages/ReportsPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('landing');
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>(null);

  // Sync tab with URL hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (['landing', 'dashboard', 'detect', 'history', 'reports'].includes(hash)) {
        setActiveTab(hash);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const changeTab = (tab: string) => {
    setActiveTab(tab);
    window.location.hash = `#/${tab}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectDetection = (id: string) => {
    setSelectedDetectionId(id);
    changeTab('detect');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-amber-500 selection:text-slate-950">
      <Navbar activeTab={activeTab} setActiveTab={changeTab} />

      <main className="flex-1">
        {activeTab === 'landing' && (
          <LandingPage
            onStartDetection={() => changeTab('detect')}
            onViewDashboard={() => changeTab('dashboard')}
          />
        )}

        {activeTab === 'dashboard' && (
          <DashboardPage
            onSelectDetection={handleSelectDetection}
            onNavigateDetect={() => changeTab('detect')}
          />
        )}

        {activeTab === 'detect' && (
          <DetectionPage
            initialDetectionId={selectedDetectionId}
            onClearInitialId={() => setSelectedDetectionId(null)}
          />
        )}

        {activeTab === 'history' && (
          <HistoryPage onSelectDetection={handleSelectDetection} />
        )}

        {activeTab === 'reports' && <ReportsPage />}
      </main>

      <Footer />
    </div>
  );
};

export default App;

