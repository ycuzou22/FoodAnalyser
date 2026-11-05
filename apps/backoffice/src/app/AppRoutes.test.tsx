import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderApp } from '../test/renderApp';

describe('routage du back-office', () => {
  it('redirige vers /login quand aucun administrateur n’est connecté', () => {
    renderApp('/foods', null);

    expect(screen.getByRole('heading', { name: 'Connexion' })).toBeInTheDocument();
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
  });

  it('protège toutes les routes du back-office, y compris les adresses inconnues', () => {
    for (const path of ['/', '/moderation', '/content', '/dashboard', '/users', '/inconnue']) {
      const { unmount } = renderApp(path, null);
      expect(screen.getByRole('heading', { name: 'Connexion' })).toBeInTheDocument();
      unmount();
    }
  });

  it('ouvre le module Aliments par défaut', () => {
    renderApp('/');

    expect(screen.getByRole('heading', { name: 'Aliments' })).toBeInTheDocument();
  });

  it('affiche les cinq modules pour un administrateur et navigue entre eux', async () => {
    renderApp('/foods');
    const nav = screen.getByRole('navigation', { name: 'Navigation principale' });

    for (const label of ['Aliments', 'Modération', 'Contenus', 'Tableau de bord', 'Utilisateurs']) {
      expect(nav).toHaveTextContent(label);
    }

    await userEvent.click(screen.getByRole('link', { name: 'Tableau de bord' }));
    expect(screen.getByRole('heading', { name: 'Tableau de bord' })).toBeInTheDocument();
  });

  it('affiche une page 404 pour une adresse inconnue', () => {
    renderApp('/inconnue');

    expect(screen.getByRole('heading', { name: 'Page introuvable' })).toBeInTheDocument();
  });
});
