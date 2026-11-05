import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useTheme } from '../theme/useTheme';

export function ErrorScreen({ onRetry }: { onRetry: () => void }) {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Text
        accessibilityRole="header"
        style={[theme.typography.title, { color: theme.colors.text }]}
      >
        {t('error.title')}
      </Text>
      <Text style={[theme.typography.body, styles.body, { color: theme.colors.textMuted }]}>
        {t('error.body')}
      </Text>
      <Pressable
        accessibilityRole="button"
        onPress={onRetry}
        style={[styles.button, { backgroundColor: theme.colors.primary }]}
      >
        <Text style={[theme.typography.body, { color: theme.colors.onPrimary }]}>
          {t('common.retry')}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 16 },
  body: { textAlign: 'center' },
  button: {
    minHeight: 48,
    minWidth: 160,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
  },
});
