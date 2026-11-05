import './i18n';

import { NavigationContainer } from '@react-navigation/native';
import { QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { connectQueryManagers, createQueryClient } from './api/queryClient';
import { ErrorBoundary } from './components/ErrorBoundary';
import { OfflineBanner } from './components/OfflineBanner';
import { RootNavigator } from './navigation/RootNavigator';
import { useSession } from './store/session';
import { useTheme } from './theme/useTheme';

export function App() {
  const [queryClient] = useState(createQueryClient);
  const theme = useTheme();
  const restore = useSession((state) => state.restore);

  useEffect(() => connectQueryManagers(), []);
  useEffect(() => {
    void restore();
  }, [restore]);

  return (
    <SafeAreaProvider>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <NavigationContainer theme={theme.navigation}>
            <StatusBar style={theme.scheme === 'dark' ? 'light' : 'dark'} />
            <OfflineBanner />
            <RootNavigator />
          </NavigationContainer>
        </QueryClientProvider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}
