# Guizmo25

Script pour extraire automatiquement les fichiers **figuremap** et **figuredata** depuis un bundle Nitro.

## Utilisation

```bash
python3 scripts/add_habbo_clothing.py /chemin/vers/mon.fichier.nitro --output ./habbo_assets
```

Le script crée automatiquement deux dossiers :

- `figuremap/`
- `figuredata/`

Si vous passez un dossier Nitro (déjà extrait), il cherchera les fichiers `figuremap.*` et `figuredata.*` directement dedans.
