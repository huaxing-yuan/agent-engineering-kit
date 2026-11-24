# Agent Engineering Kit

**Mémoire de projet et vérification, intégrées au dépôt, pour les agents de code.**

Agent Engineering Kit donne à un agent de code ce qu'une session neuve ne peut pas déduire du seul code source : plans actifs, décisions durables, maturité des modules, stratégies de vérification, responsabilité des tests manuels et définition de terminé contrôlée par une machine.

Le kit est indépendant de l'agent hôte. Il fonctionne avec tout agent capable de lire les fichiers du dépôt et d'exécuter des commandes.

- English: [README.md](README.md)
- Français: ce fichier
- 中文: [README.zh-CN.md](README.zh-CN.md)

## Ce qu'il est

- Un ensemble compact de contrats Markdown et de modèles.
- Une CLI Python qui découvre la structure du projet, initialise sans écraser, génère les index, valide les écritures de suivi et produit un rapport de progression.
- Un modèle de vérification qui distingue tests unitaires, d'intégration, headless, processus réel, services externes et vérification manuelle.
- Un parcours d'adoption qui préserve les `AGENTS.md`, `CLAUDE.md`, instructions et documents d'ingénierie existants.

## Ce qu'il n'est pas

- Ce n'est ni un runtime d'agent, ni un modèle, ni un orchestrateur, ni une file de tâches.
- Cela ne remplace pas GitHub Issues, Jira ou Linear.
- Cela n'impose aucun langage, framework ou cloud.
- Cela ne rend pas un agent autonome et ne transforme pas un build vert en preuve qu'une fonctionnalité marche.

## L'idée centrale

> Le code dit ce que fait le système. La mémoire du dépôt dit ce que l'équipe veut, ce qu'elle a refusé et quelles preuves manquent encore.

| Artefact | Responsabilité |
|---|---|
| `AGENTS.md` | Contrat permanent de l'agent |
| `engineering/modules/` | Maturité, documentation, tests et feuille de route |
| `engineering/plans/` | Contrats d'exécution actifs et tranches atomiques |
| `engineering/decisions/` | Décisions acceptées, refusées, différées ou remplacées |
| `engineering/manual-tests/` | Contrôles que l'automatisation ne peut pas exercer aujourd'hui |
| `engineering/verification/` | Matrice de tests et exceptions temporaires |
| `aeng check` | Porte de terminé détectant les écritures manquantes ou périmées |

## Prérequis

- Python 3.10 ou plus récent.
- PyYAML 6.x.
- Git pour la sélection des tests par changement.
- GitHub CLI uniquement si vous utilisez explicitement `aeng verify add --create-issue` ou `--close-issue`.

Aucune clé d'API de modèle n'est nécessaire.

## Démarrage rapide

### 1. Exécuter le kit lui-même

```bash
git clone https://github.com/<votre-compte>/agent-engineering-kit.git
cd agent-engineering-kit

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1

python -m pip install -e .
aeng --version
aeng check
aeng report
```

Remplacez `<votre-compte>` par le compte depuis lequel vous avez fait le fork. L'emplacement public canonique de ce dépôt est :

```bash
git clone https://github.com/huaxing-yuan/agent-engineering-kit.git
```

### 2. Utiliser le kit dans un projet existant

Installez la CLI depuis votre fork local, puis lancez la découverte dans le projet cible :

```bash
python -m pip install -e /chemin/vers/agent-engineering-kit
cd /chemin/vers/votre-projet

aeng discover --output .agent-engineering.yaml
```

Relisez le fichier généré avant l'initialisation. La découverte est une proposition, pas une décision d'architecture. Corrigez :

- nom, description et langages du projet ;
- racines sources et frontières des modules ;
- commandes de test, build et lint ;
- fichiers d'instructions existants ;
- racine et langues de la documentation ;
- nécessité de tests UI/headless ;
- obligation ou non de créer une issue pour les tests manuels.

Prévisualisez puis appliquez :

```bash
aeng init --dry-run
aeng init
aeng check
aeng report
```

`aeng init` n'écrase jamais un `AGENTS.md`, `CLAUDE.md`, fichier d'instructions, carte de module ou document d'ingénierie existant. Si `engineering/` existe déjà, utilisez `--adopt-existing` pour n'ajouter que les fichiers manquants.

## Faire initialiser le projet par un agent de code

Après installation de la CLI, donnez ce prompt à votre agent :

```text
Initialise agent-engineering-kit dans ce dépôt.

1. Exécute `aeng discover --stdout` et inspecte les manifests, l'arborescence source, les tests, la documentation, AGENTS.md, CLAUDE.md et les instructions existantes.
2. Crée ou mets à jour .agent-engineering.yaml avec les langages, racines sources, frontières de modules, responsabilités et commandes de test/build/lint réels.
3. N'écrase aucune règle d'agent ni aucun artefact d'ingénierie existant.
4. Exécute `aeng init --dry-run` et présente le plan d'adoption et les conflits.
5. Attends mon approbation, puis exécute `aeng init` (utilise --adopt-existing seulement si j'approuve l'adoption d'un engineering/ existant).
6. Exécute `aeng check`, corrige uniquement les problèmes d'initialisation, puis `aeng report`.
7. Résume ce qui a été installé, préservé, ce qui demande une revue et quelles commandes restent inconnues.
```

L'agent doit inspecter le dépôt, pas inventer les frontières de modules ni annoncer des commandes de test réussies.

## Ce que l'initialisation crée

```text
AGENTS.md                              # seulement s'il est absent
CLAUDE.md                              # seulement s'il est absent
.github/instructions/agent-engineering/
  README.md
  core-engineering.md
  testing.md
  ui.md
  documentation.md
  security.md
  git-and-sessions.md
engineering/
  README.md
  PROJECT.md                           # généré
  modules/<module-id>.md
  plans/INDEX.yaml                     # généré
  decisions/README.md                  # index généré
  manual-tests/README.md               # backlog ouvert généré
  verification/test-matrix.yaml
  verification/known-failures.yaml
  technical/_TEMPLATE.md
  reports/_TEMPLATE.md
.agent-engineering/
  adoption-report.md
  integration-block.md                 # si un contrat d'agent existant a été préservé
```

Les instructions existantes ne sont ni déplacées ni réécrites. Celles du kit vivent dans un répertoire dédié afin de coexister avec les règles du projet ou de l'hôte.

## Cycle de vie d'un plan

Ouvrez un plan lorsque le travail traverse plusieurs sessions ou tranches, plusieurs modules, un contrat public, une migration ou des portes ordonnées. Utilisez une `investigation` limitée dans le temps si l'approche reste incertaine.

```text
draft -> in-progress -> dev-finished -> done -> retired
              |              |
           blocked       vérification manuelle
              |
        superseded / abandoned
```

Un plan contient des tranches atomiques :

| ID | Scope | Verification | Status | Evidence |
|---|---|---|---|---|
| S1 | Contrat de domaine | Unit + contract tests | landed | commit/test link |
| S2 | Comportement UI | Headless test | in-progress | — |

Règles :

- La progression est calculée depuis les tranches ; aucun pourcentage n'est saisi à la main.
- Une tranche avec un reste inachevé n'est pas `landed`.
- `landed` exige une preuve.
- `dev-finished` signifie que toutes les tranches sont terminées et qu'il ne reste que la vérification humaine ou la documentation requise.
- Un plan est retiré après tests, impact documentaire, vérification manuelle et décisions durables.
- Les plans terminés sont supprimés ; l'historique Git constitue l'archive.

## Décisions

Écrivez une décision lorsqu'une direction durable est acceptée, refusée, différée ou remplacée. N'utilisez pas le registre comme journal des modifications.

Les identifiants utilisent `dec-YYYY-MM-DD-kebab-case-title`, ce qui évite les collisions de numérotation entre agents parallèles. Une décision contient le contexte, la règle, les conséquences et la preuve qui permettrait de la rouvrir. `enforced_by` peut pointer vers un test ou un garde-fou.

## Issues et tests manuels

- Les rapports de bug externes et le travail à trier indépendamment vont dans les issues.
- Une petite correction dans un plan actif n'a pas besoin d'une issue duplicate.
- Ajoutez un test manuel lorsque l'automatisation actuelle ne peut pas exercer le changement.
- Les nouveaux tests manuels exigent une issue par défaut. Mettez `github.issue_required: false` sans gestionnaire d'issues.
- Seule une confirmation humaine explicite permet `verified` ; renseignez le build exact dans `verified_in`.
- Lorsqu'un contrôle devient automatisable, ajoutez le test et marquez l'entrée `obsolete`.

## Modèle de vérification

| Couche | Usage |
|---|---|
| Static/governance | Format, liens, schémas, index, écritures manquantes |
| Unit | Logique pure et cas limites |
| Component/contract | Frontières, sérialisation, compatibilité |
| Integration | Plusieurs modules et dépendances éphémères |
| Headless/in-process | Comportement réel de l'application et de l'UI sans chrome OS |
| Real-process E2E | Packaging, dialogues OS, focus, multi-fenêtres, accessibilité |
| Live external | Vrais fournisseurs, comptes, réseaux et modèles payants |
| Manual | Jugement visuel, nuance linguistique, matériel, comptes réels |

Règles importantes :

1. Prouvez qu'un test de régression échoue sur l'ancien comportement.
2. La sélection des tests est une optimisation, pas une preuve de couverture complète.
3. Les changements larges ou d'infrastructure utilisent la porte fast/full.
4. `0 tests executed` n'est pas un succès.
5. Attendez un état observable, pas un délai fixe.
6. Utilisez des identifiants d'automatisation stables, pas des libellés localisés.
7. Une capture d'écran est un artefact, pas une assertion de comportement.
8. Un échec connu exige un test exact, un owner, une issue, un motif et une date d'expiration.

Si le dépôt contient un produit agent, ajoutez une piste d'évaluation orthogonale pour les schémas d'outils, la visibilité des rôles, les permissions, les confirmations, les trajectoires de référence et les artefacts finaux.

## Réutilisation et précautions

### À réutiliser directement

- Cycle de vie plan/décision/test manuel.
- Tranches atomiques avec preuves.
- Index générés et contrôle de terminé.
- Routage des tests par couche.
- Initialisation sûre préservant les fichiers existants.
- Exceptions temporaires avec expiration.

### À adapter

- Frontières et propriété des modules.
- Commandes de test, build et lint.
- Emplacement et langues de la documentation.
- Définitions de maturité et seuils de revue.
- Politique bloquante de la CI.
- Labels et intégration du gestionnaire d'issues.

### À utiliser avec précaution

- **`AGENTS.md` existant** : fusionnez le bloc d'intégration volontairement.
- **`engineering/` existant** : adoptez progressivement et migrez le frontmatter avant de faire confiance à la porte.
- **Tests UI headless** : le support et la couverture OS varient.
- **Tests live** : identifiants, coût, limites de débit et nondéterminisme exigent des contrôles explicites.
- **Échecs connus** : une allowlist peut devenir une dette permanente ; l'expiration est obligatoire.
- **Numérotation globale des décisions** : ne l'introduisez pas dans un nouveau dépôt.
- **Décisions historiques** : ne publiez jamais des décisions privées comme exemples génériques.
- **Rapports et captures** : retirez données clients, hôtes internes, tokens et métadonnées.

Voir [docs/ADOPTION_GUIDE.md](docs/ADOPTION_GUIDE.md).

## Référence CLI

| Commande | Objectif |
|---|---|
| `aeng discover` | Proposer une configuration depuis les fichiers et manifests |
| `aeng init --dry-run` | Prévisualiser créations et préservations |
| `aeng init` | Installer uniquement les contrats et artefacts manquants |
| `aeng init --adopt-existing` | Compléter un `engineering/` existant |
| `aeng check` | Échouer sur un artefact invalide ou périmé |
| `aeng index` | Régénérer les index et `PROJECT.md` |
| `aeng report` | Afficher la progression dérivée |
| `aeng plan new` | Créer un plan actif |
| `aeng plan add-slice` | Ajouter une tranche atomique |
| `aeng plan set-slice` | Mettre à jour statut et preuve |
| `aeng plan status` | Faire avancer le cycle de vie |
| `aeng plan retire` | Supprimer un plan terminé après validation |
| `aeng decision add` | Enregistrer une décision durable |
| `aeng verify add` | Ajouter un contrôle manuel, avec issue optionnelle |
| `aeng verify close` | Enregistrer une vérification humaine explicite |
| `aeng test select` | Afficher les tests probables et le motif de fallback |
| `aeng test select --run` | Exécuter les commandes configurées |

Utilisez `aeng <command> --help`. Placez l'option globale `--root` avant la commande pour un autre répertoire.

## Documentation

- [Quick start](docs/QUICKSTART.md)
- [Prompt d'initialisation](docs/AGENT_INITIALIZATION.md)
- [Guide d'adoption](docs/ADOPTION_GUIDE.md)
- [Configuration](docs/CONFIGURATION.md)
- [Cycle de vie](docs/LIFECYCLE.md)
- [Stratégie de tests](docs/TESTING.md)
- [Sécurité](SECURITY.md)
- [Contribution](CONTRIBUTING.md)

## Limites actuelles

La version 0.1 est volontairement petite :

- La sélection des tests est basée sur les chemins, pas sur un graphe de dépendances.
- L'analyse des tranches Markdown attend la forme documentée du tableau.
- L'intégration GitHub utilise la CLI et reste optionnelle ; il n'y a pas de service de synchronisation.
- Pas de GUI, de dashboard hébergé ni de workflow multi-dépôt `moved`.
- Les schémas JSON ne sont pas encore livrés ; la validation vit dans la CLI et les tests.
- L'exemple est synthétique et ne prouve pas l'adéquation à toutes les stacks.

## Contribution

Lisez [CONTRIBUTING.md](CONTRIBUTING.md). Un changement de sémantique de cycle de vie exige des tests et une décision. Un changement de modèle exige un test d'initialisation propre et un test de préservation d'un projet existant.

## Licence

[MIT](LICENSE).
