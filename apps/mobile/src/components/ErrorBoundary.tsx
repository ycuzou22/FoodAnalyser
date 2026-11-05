import { Component, type ErrorInfo, type ReactNode } from 'react';

import { ErrorScreen } from '../screens/ErrorScreen';

interface State {
  hasError: boolean;
}

/** Écran d'erreur générique plutôt qu'un écran blanc si un composant plante. */
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Envoyé à Sentry avec l'issue #53, sans données de l'utilisateur.
    if (__DEV__) console.error(error, info.componentStack);
  }

  private readonly reset = () => this.setState({ hasError: false });

  render() {
    return this.state.hasError ? <ErrorScreen onRetry={this.reset} /> : this.props.children;
  }
}
