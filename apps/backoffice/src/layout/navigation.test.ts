import { NAVIGATION, visibleNavigation } from './navigation';

describe('menu selon les rôles', () => {
  it('montre tout à un administrateur', () => {
    expect(visibleNavigation(['admin'])).toEqual(NAVIGATION);
  });

  it('limite un analyste au tableau de bord', () => {
    expect(visibleNavigation(['analyst']).map((item) => item.path)).toEqual(['/dashboard']);
  });

  it('cumule les droits de plusieurs rôles', () => {
    const paths = visibleNavigation(['nutrition_editor', 'content_editor']).map((i) => i.path);
    expect(paths).toEqual(['/foods', '/moderation', '/content']);
  });

  it('ne montre rien sans rôle', () => {
    expect(visibleNavigation([])).toEqual([]);
  });
});
