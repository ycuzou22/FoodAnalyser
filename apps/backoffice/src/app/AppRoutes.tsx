import { Navigate, Route, Routes } from 'react-router';

import { PlaceholderPage } from '../components/PlaceholderPage';
import { RequireAuth } from '../features/auth/RequireAuth';
import { AdminLayout } from '../layout/AdminLayout';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/foods" replace />} />
        <Route path="foods" element={<PlaceholderPage title="Aliments" issue={35} />} />
        <Route path="moderation" element={<PlaceholderPage title="Modération" issue={51} />} />
        <Route path="content" element={<PlaceholderPage title="Contenus" issue={48} />} />
        <Route path="dashboard" element={<PlaceholderPage title="Tableau de bord" issue={52} />} />
        <Route path="users" element={<PlaceholderPage title="Utilisateurs" issue={34} />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
