# Sources des données nutritionnelles

La table `foods` est alimentée par deux sources ouvertes. Les fichiers sources ne sont **jamais commités** : on les dépose dans `data/foods/` (ignoré par Git) puis on lance l'import.

| Source | Contenu | Licence | Clé d'unicité | Volume attendu |
| --- | --- | --- | --- | --- |
| [Table Ciqual](https://ciqual.anses.fr/) (Anses) | Aliments génériques (« banane crue », « pâtes cuites ») | [Licence Ouverte / Open Licence 2.0](https://www.data.gouv.fr/fr/datasets/table-de-composition-nutritionnelle-des-aliments-ciqual/) | `ciqual_code` | ~3 500 aliments (3 484 dans la version de novembre 2025) |
| [Open Food Facts](https://world.openfoodfacts.org/data) | Produits emballés, par code-barres | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) (base), DbCL 1.0 (contenus) | `barcode` | > 100 000 produits vendus en France |

## Attribution (obligatoire)

L'application et le site doivent afficher, dans les mentions légales et sur la fiche d'un aliment :

- « Données de composition : Anses, Table de composition nutritionnelle des aliments Ciqual. »
- « Données produits : Open Food Facts, sous licence ODbL — https://world.openfoodfacts.org »

L'ODbL impose en outre que toute base dérivée redistribuée reste sous ODbL. FoodAnalyser ne redistribue pas la base : l'usage interne pour calculer les apports est permis, mais **un export public de la table `foods` ne l'est qu'en ODbL**.

## Importer

```bash
mkdir -p data/foods
# Déposer les fichiers téléchargés :
#   data/foods/ciqual.xls   (ou .xlsx / .csv)   → https://ciqual.anses.fr
#   data/foods/en.openfoodfacts.org.products.csv.gz → https://world.openfoodfacts.org/data

make import-foods CIQUAL=ciqual.xls CIQUAL_VERSION=2025 OFF=en.openfoodfacts.org.products.csv.gz OFF_VERSION=2026-11-05
```

Hors Docker : `cd services/api && uv run python -m app.scripts.import_foods {ciqual|off} <fichier> --version <v> [--limit N]`.

L'import est **idempotent** : relancer le même fichier met à jour les aliments existants sans doublon. Chaque import est tracé dans `food_source_imports` (source, version, licence, volumes, motifs de rejet). Une ligne dont `finished_at` est vide signale un import interrompu.

## Règles de lecture

| Cas | Traitement |
| --- | --- |
| Décimales « 12,5 » ou « 12.5 » | 12,5 |
| « - », vide, « ND » | valeur inconnue |
| « traces » | 0 |
| « < 0,5 » (sous la limite de quantification) | moitié du seuil : 0,25 |
| Énergie absente en kcal | calculée depuis les kJ (÷ 4,184) |
| CIQUAL : énergie | colonne « Énergie, Règlement UE 1169/2011 » (référence d'étiquetage), jamais « N x facteur Jones » |
| CIQUAL : protéines | « N x facteur de Jones » en priorité, sinon « N x 6,25 » |
| OFF : nom | nom français, sinon nom par défaut |
| OFF : Nutri-Score `unknown`, `not-applicable` | ignoré |
| OFF : popularité | `unique_scans_n` (sert au classement de la recherche, #27) |
| Même code-barres deux fois | la dernière occurrence l'emporte |

Les colonnes CIQUAL sont repérées par motif (français ou anglais), pas par intitulé exact, car les libellés changent d'une version à l'autre. Si une colonne indispensable manque, l'import s'arrête **avant d'écrire quoi que ce soit** et affiche les en-têtes lus.

## Rejets

| Motif | Signification |
| --- | --- |
| `missing_name` | Nom vide |
| `missing_ciqual_code` / `invalid_barcode` | Identifiant absent, ou code-barres dont la clé de contrôle est fausse |
| `missing_kcal` / `kcal_out_of_range` | Énergie absente, ou hors de 0 à 900 kcal / 100 g |
| `missing_macros` | Protéines, glucides ou lipides manquants |
| `nutrient_out_of_range` | Un nutriment hors de 0 à 100 g / 100 g |
| `macros_exceed_100g` | Protéines + glucides + lipides > 102 g (tolérance d'arrondi de 2 g) |
| `invalid_nutriscore` | Note hors de a à e |

Le rapport d'import affiche le nombre de lignes rejetées par motif ; un taux anormal (par exemple beaucoup de `missing_kcal` sur CIQUAL) indique un changement de format de la source.
