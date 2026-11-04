# Référentiel des exigences

Extrait du cahier des charges (version du 4 novembre 2026). Les issues GitHub citent ces identifiants. Priorités MoSCoW : M = MVP, S = V1, C = plus tard.

## Exigences fonctionnelles

### Compte et profil

| ID | Exigence | Prio |
| --- | --- | --- |
| F-01 | Inscription e-mail, Apple, Google | M |
| F-02 | Questionnaire d'onboarding et calcul des besoins (Mifflin-St Jeor + activité) | M |
| F-03 | Choix de l'objectif : perte, maintien, prise de masse, rééquilibrage | M |
| F-04 | Préférences alimentaires : végétarien, vegan, sans gluten, halal, allergies | S |
| F-05 | Export et suppression des données (RGPD) | M |
| F-06 | Gestion multi-unités (kg/lb, kcal/kJ) | S |

### Reconnaissance et saisie des repas

| ID | Exigence | Prio |
| --- | --- | --- |
| F-10 | Photo d'une assiette → détection de plusieurs aliments | M |
| F-11 | Estimation automatique de la portion (grammes) | M |
| F-12 | Correction rapide : remplacer un aliment, ajuster la quantité | M |
| F-13 | Scan de code-barres (Open Food Facts) | M |
| F-14 | Recherche textuelle dans la base d'aliments | M |
| F-15 | Saisie vocale | C |
| F-16 | Repas favoris et récents en un clic | S |
| F-17 | Recettes maison avec calcul par portion | S |
| F-18 | Mode hors ligne : photo analysée à la reconnexion | S |

### Journal et suivi

| ID | Exigence | Prio |
| --- | --- | --- |
| F-20 | Journal par jour et par repas | M |
| F-21 | Jauge calories et macros restantes | M |
| F-22 | Suivi du poids avec courbe | M |
| F-23 | Suivi de l'hydratation | S |
| F-24 | Statistiques hebdomadaires et mensuelles | S |
| F-25 | Score de qualité du repas (équilibre, Nutri-Score) | S |
| F-26 | Micronutriments | C |

### Accompagnement

| ID | Exigence | Prio |
| --- | --- | --- |
| F-30 | Notifications de rappel des repas paramétrables | M |
| F-31 | Conseils contextuels après chaque repas | S |
| F-32 | Programmes thématiques de 2 à 8 semaines | S |
| F-33 | Bibliothèque de recettes filtrables | S |
| F-34 | Messagerie avec un diététicien (premium) | C |
| F-35 | Assistant conversationnel nutrition (LLM encadré) | C |

### Intégrations

| ID | Exigence | Prio |
| --- | --- | --- |
| F-40 | Apple Santé et Health Connect : poids, pas, dépense énergétique | S |
| F-41 | Import d'activité Strava, Garmin | C |

### Monétisation

| ID | Exigence | Prio |
| --- | --- | --- |
| F-50 | Abonnement in-app (App Store, Google Play) | M |
| F-51 | Essai gratuit de 7 jours | M |
| F-52 | Paywall configurable à distance | S |

### Back-office

| ID | Exigence | Prio |
| --- | --- | --- |
| F-60 | Gestion de la base d'aliments (ajout, correction, fusion de doublons) | M |
| F-61 | Modération des corrections remontées par les utilisateurs | S |
| F-62 | Gestion des contenus (recettes, programmes, articles) | S |
| F-63 | Tableau de bord métier (actifs, conversion, rétention) | S |
| F-64 | Gestion des comptes diététiciens | C |

## Exigences non fonctionnelles

| ID | Domaine | Cible |
| --- | --- | --- |
| NFR-01 | Analyse photo (envoi → résultat) | < 3 s au p95 en 4G |
| NFR-02 | Démarrage à froid de l'app | < 2 s sur un appareil de 3 ans |
| NFR-03 | Réponse API hors IA | < 300 ms au p95 |
| NFR-04 | Disponibilité | 99,5 % mensuel |
| NFR-05 | Pics aux heures de repas | Montée en charge automatique ×5 |
| NFR-06 | Compatibilité | iOS 16+, Android 9+ |
| NFR-07 | Accessibilité | RGAA / WCAG 2.1 AA |
| NFR-08 | Langues | Français au lancement, puis anglais, espagnol |
| NFR-09 | Hors ligne | Journal consultable sans réseau |
| NFR-10 | Taille de l'app | < 80 Mo installée |
| NFR-11 | Couverture de tests | > 70 % back-end |
| NFR-12 | Observabilité | Alerte < 5 min |

## Exigences IA

| ID | Indicateur | Cible V1 |
| --- | --- | --- |
| IA-01 | Précision top-1 | ≥ 80 % |
| IA-02 | Précision top-3 | ≥ 93 % |
| IA-03 | Erreur moyenne sur les calories d'un repas | ≤ 20 % |
| IA-04 | Taux de correction utilisateur | < 30 % des aliments |

## Sécurité et conformité

| ID | Exigence |
| --- | --- |
| SEC-01 | Consentement explicite et granulaire (données de santé, entraînement IA, analytics, marketing) |
| SEC-02 | AIPD et registre des traitements avant lancement |
| SEC-03 | Chiffrement au repos AES-256 et par colonne des données de santé |
| SEC-04 | OAuth 2.0 / OIDC, JWT courte durée, refresh token rotatif, MFA back-office |
| SEC-05 | TLS 1.3, certificate pinning mobile |
| SEC-06 | Rate limiting, validation des entrées, contrôle d'appartenance (anti-IDOR) |
| SEC-07 | Upload : contrôle MIME, 10 Mo max, suppression EXIF |
| SEC-08 | SAST, SCA, DAST en CI ; pentest avant lancement (OWASP MASVS, API Top 10) |
| SEC-09 | Sauvegardes chiffrées quotidiennes, RPO 24 h, RTO 4 h |
| REG-01 | Seuils caloriques minimaux (1 200 / 1 500 kcal), perte ≤ 1 kg/semaine |
| REG-02 | Détection de signaux de troubles alimentaires et orientation |
| REG-03 | Accès réservé aux 18 ans et plus |
| REG-04 | Transparence IA (AI Act), pas d'allégation de santé |
| REG-05 | Résiliation de l'abonnement en trois clics |
