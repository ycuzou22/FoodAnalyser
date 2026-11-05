import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useTranslation } from 'react-i18next';
import { StyleSheet, Text, View } from 'react-native';

import { CameraScreen, JournalScreen, ProfileScreen, RecipesScreen, StatsScreen } from '../screens';
import { useTheme } from '../theme/useTheme';
import type { MainTabParamList } from './types';

const Tab = createBottomTabNavigator<MainTabParamList>();

/** Bouton central mis en avant : l'action principale de l'app (section 12 du cahier des charges). */
function CameraTabIcon({ focused }: { focused: boolean }) {
  const theme = useTheme();
  return (
    <View
      style={[
        styles.cameraButton,
        { backgroundColor: theme.colors.primary, opacity: focused ? 1 : 0.9 },
      ]}
    >
      <Text style={[styles.cameraGlyph, { color: theme.colors.onPrimary }]}>+</Text>
    </View>
  );
}

export function MainTabs() {
  const { t } = useTranslation();
  return (
    <Tab.Navigator initialRouteName="Journal" screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Journal" component={JournalScreen} options={{ title: t('tabs.journal') }} />
      <Tab.Screen name="Stats" component={StatsScreen} options={{ title: t('tabs.stats') }} />
      <Tab.Screen
        name="Camera"
        component={CameraScreen}
        options={{
          title: t('tabs.camera'),
          tabBarAccessibilityLabel: t('tabs.cameraHint'),
          tabBarIcon: CameraTabIcon,
          tabBarShowLabel: false,
        }}
      />
      <Tab.Screen name="Recipes" component={RecipesScreen} options={{ title: t('tabs.recipes') }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: t('tabs.profile') }} />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  cameraButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  cameraGlyph: { fontSize: 30, lineHeight: 32, fontWeight: '600' },
});
