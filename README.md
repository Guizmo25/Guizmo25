# Habbo Nitro Clothing Installer

Ce dépôt contient un script pour installer automatiquement des vêtements Habbo
à partir d'un fichier `.nitro` : copie des dossiers **figuremap**, **figuredata**
(et **data**) + application des fichiers SQL.

## Prérequis

- Python 3.9+
- (Optionnel) client MySQL (`mysql`) pour appliquer les scripts SQL

## Utilisation rapide

```bash
python3 install_nitro_clothing.py /chemin/vers/pack.nitro \
  --server-root /chemin/vers/ton/serveur \
  --db-user habbo --db-pass secret --db-name habbo
```

Le script cherche automatiquement :

- `figuremap.xml` ou un dossier `figuremap/`
- `figuredata.xml` ou un dossier `figuredata/`
- un dossier `data/` (ou `gamedata/`)
- tous les fichiers `.sql`

## Options utiles

- `--server-root`: crée automatiquement `figuremap/`, `figuredata/` et `data/`.
- `--figuremap-dir`, `--figuredata-dir`, `--data-dir`: chemins personnalisés.
- `--mysql-bin`: chemin vers le binaire `mysql` si nécessaire.

## Exemple avec chemins personnalisés

```bash
python3 install_nitro_clothing.py pack.nitro \
  --figuremap-dir /srv/habbo/figuremap \
  --figuredata-dir /srv/habbo/figuredata \
  --data-dir /srv/habbo/data
```
