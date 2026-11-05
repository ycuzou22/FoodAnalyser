import { useTranslation } from 'react-i18next';

import { PlaceholderScreen } from './PlaceholderScreen';

// Écrans provisoires : chacun est remplacé par l'issue indiquée dans fr.json.

export function JournalScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('screens.journal.title')} note={t('screens.journal.issue')} />;
}

export function StatsScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('screens.stats.title')} note={t('screens.stats.issue')} />;
}

export function CameraScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('screens.camera.title')} note={t('screens.camera.issue')} />;
}

export function RecipesScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('screens.recipes.title')} note={t('screens.recipes.issue')} />;
}

export function ProfileScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('screens.profile.title')} note={t('screens.profile.issue')} />;
}

export function WelcomeScreen() {
  const { t } = useTranslation();
  return <PlaceholderScreen title={t('welcome.title')} note={t('welcome.issue')} />;
}
