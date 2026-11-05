import { onlineManager } from '@tanstack/react-query';
import { useSyncExternalStore } from 'react';

/** Vrai tant que le téléphone a du réseau (source : NetInfo via TanStack Query). */
export function useIsOnline(): boolean {
  return useSyncExternalStore(
    (onChange) => onlineManager.subscribe(onChange),
    () => onlineManager.isOnline(),
  );
}
