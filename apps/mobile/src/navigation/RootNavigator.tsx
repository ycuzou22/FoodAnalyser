import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import { WelcomeScreen } from '../screens';
import { useSession } from '../store/session';
import { useTheme } from '../theme/useTheme';
import { MainTabs } from './MainTabs';
import type { AuthStackParamList } from './types';

const AuthStack = createNativeStackNavigator<AuthStackParamList>();

/** Choisit le parcours selon la session : connexion ou application. */
export function RootNavigator() {
  const status = useSession((state) => state.status);
  const theme = useTheme();

  if (status === 'loading') {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator color={theme.colors.primary} />
      </View>
    );
  }
  if (status === 'signedIn') return <MainTabs />;
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Welcome" component={WelcomeScreen} />
    </AuthStack.Navigator>
  );
}
