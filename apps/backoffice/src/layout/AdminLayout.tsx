import { AppShell, Burger, Group, NavLink, Text, Title } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { NavLink as RouterNavLink, Outlet } from 'react-router';

import { useAuth } from '../features/auth/auth';
import { visibleNavigation } from './navigation';

export function AdminLayout() {
  const [opened, { toggle }] = useDisclosure();
  const { user } = useAuth();
  const items = visibleNavigation(user?.roles ?? []);

  return (
    <AppShell
      header={{ height: 56 }}
      navbar={{ width: 240, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" aria-label="Menu" />
            <Title order={4}>FoodAnalyser · Administration</Title>
          </Group>
          <Text size="sm" c="dimmed">
            {user?.email}
          </Text>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="sm" aria-label="Navigation principale">
        {items.map((item) => (
          <NavLink key={item.path} component={RouterNavLink} to={item.path} label={item.label} />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
