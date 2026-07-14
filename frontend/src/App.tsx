import { Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './layout/Layout';
import { ChatPage } from './pages/ChatPage';
import { RepositoryPage } from './pages/RepositoryPage';
import { HistoryPage } from './pages/HistoryPage';
import { ModelsPage } from './pages/ModelsPage';
import { VectorStorePage } from './pages/VectorStorePage';
import { LogsPage } from './pages/LogsPage';
import { ApiKeysPage } from './pages/ApiKeysPage';
import { SettingsPage } from './pages/SettingsPage';
import { AccountPage } from './pages/AccountPage';

function App() {
  return (
    <Layout>
      <Routes>
        {/* Home → repository (dashboard default) */}
        <Route path="/" element={<Navigate to="/repository" replace />} />
        <Route path="/repository" element={<RepositoryPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route path="/vector-store" element={<VectorStorePage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/api-keys" element={<ApiKeysPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/account" element={<AccountPage />} />
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/repository" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
