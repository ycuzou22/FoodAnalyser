import { StyleSheet, Text, View } from 'react-native';

import { useTheme } from '../theme/useTheme';

/** Écran provisoire d'une fonctionnalité, remplacé par l'issue qui l'implémente. */
export function PlaceholderScreen({ title, note }: { title: string; note: string }) {
  const theme = useTheme();
  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Text
        accessibilityRole="header"
        style={[theme.typography.title, { color: theme.colors.text }]}
      >
        {title}
      </Text>
      <Text style={[theme.typography.caption, { color: theme.colors.textMuted }]}>{note}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, gap: 8 },
});
