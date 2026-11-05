import { Anchor, Stack, Text, Title } from '@mantine/core';
import { Link } from 'react-router';

export function NotFoundPage() {
  return (
    <Stack gap="xs">
      <Title order={2}>Page introuvable</Title>
      <Text c="dimmed">Cette adresse ne correspond à aucune page du back-office.</Text>
      <Anchor component={Link} to="/">
        Retour à l'accueil
      </Anchor>
    </Stack>
  );
}
