import { Center, Paper, Stack, Text, Title } from '@mantine/core';

/** Connexion administrateur. Le formulaire avec second facteur (TOTP) arrive avec l'issue #34. */
export function LoginPage() {
  return (
    <Center h="100vh">
      <Paper withBorder p="xl" radius="md" w={380}>
        <Stack>
          <Title order={2}>Connexion</Title>
          <Text c="dimmed">
            L'accès au back-office nécessitera un mot de passe et un second facteur (issue #34).
          </Text>
        </Stack>
      </Paper>
    </Center>
  );
}
