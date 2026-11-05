import { useTranslation } from 'react-i18next';
import { StyleSheet, Text, View } from 'react-native';

import { useIsOnline } from '../hooks/useIsOnline';
import { useTheme } from '../theme/useTheme';

export function OfflineBanner() {
  const isOnline = useIsOnline();
  const { t } = useTranslation();
  const theme = useTheme();

  if (isOnline) return null;
  return (
    <View
      accessibilityRole="alert"
      style={[
        styles.banner,
        { backgroundColor: theme.colors.surface, borderColor: theme.colors.notice },
      ]}
    >
      <Text style={[theme.typography.caption, { color: theme.colors.notice }]}>
        {t('offline.banner')}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: { paddingHorizontal: 16, paddingVertical: 8, borderBottomWidth: 2 },
});
