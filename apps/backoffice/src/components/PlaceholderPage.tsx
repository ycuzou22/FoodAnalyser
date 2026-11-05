import { Stack, Text, Title } from '@mantine/core';

/** Page provisoire d'un module, remplacée par l'issue qui l'implémente. */
export function PlaceholderPage({ title, issue }: { title: string; issue: number }) {
  return (
    <Stack gap="xs">
      <Title order={2}>{title}</Title>
      <Text c="dimmed">Module à venir (issue #{issue}).</Text>
    </Stack>
  );
}
