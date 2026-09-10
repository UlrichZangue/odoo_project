# Odoo 16 — Support et interventions clients

Projet portfolio démontrant la conception d'un module métier Odoo 16 : qualification des demandes d'assistance, affectation à un consultant, planification des interventions, traçabilité et compte rendu PDF. Le dépôt contient uniquement le module personnalisé et son environnement reproductible ; Odoo reste une dépendance externe fournie par son image Docker officielle.

## Fonctionnalités

- Tickets séquencés avec client, contact, catégorie, priorité, échéance et workflow en six états.
- Chatter, pièces jointes, abonnés, activités et historique des champs importants.
- Interventions à distance ou sur site, dates réelles, diagnostic, actions, résultat et validation client.
- Listes décorées, formulaires guidés, recherche, regroupements et kanban par état.
- Rapport QWeb PDF d'intervention et données de démonstration séparées.
- Activité immédiate pour un ticket urgent et rappel automatique 24 heures avant échéance.
- Trois rôles avec règles d'enregistrement et droits distincts.
- Tests transactionnels du workflow, des séquences, des contraintes, du calcul et de l'isolation des tickets.

## Architecture et technologies

Le module suit l'architecture standard Odoo : `models/` pour la logique ORM, `views/` pour l'interface, `security/` pour ACL et règles, `data/` pour séquences et tâche planifiée, `report/` pour QWeb, `demo/` et `tests/`. Technologies : Python 3, XML/QWeb, PostgreSQL, Docker Compose et Odoo 16 Community (LGPL-3).

## Démarrage avec Docker

Prérequis : Docker Engine avec le plugin Compose.

```bash
cp .env.example .env
# Remplacer les deux valeurs CHANGE_ME dans .env
docker compose up -d
docker compose ps
```

Ouvrir `http://localhost:8069`. Au premier lancement, Odoo initialise automatiquement la base indiquée par `POSTGRES_DB` et installe le module « Support et interventions clients ». Cette opération peut prendre une à deux minutes. Connectez-vous ensuite avec le compte administrateur Odoo créé pendant l'initialisation standard de l'image, puis attribuez exactement l'un des groupes Support depuis chaque fiche utilisateur.

Les données d'exemple n'existent que si la base est créée avec les données de démonstration. Elles ne contiennent aucun compte ni mot de passe. Le détail des rôles est dans [la documentation fonctionnelle](docs/functional-guide.md).

## Tests

Sur une base de test jetable et après démarrage de PostgreSQL :

```bash
docker compose run --rm odoo odoo \
  --stop-after-init \
  --database=odoo_test \
  --init=client_support_intervention \
  --test-enable \
  --test-tags=/client_support_intervention
```

La base `odoo_test` doit être supprimée ou recréée entre deux installations complètes. Les contrôles statiques locaux sont décrits dans [le guide technique](docs/technical-guide.md).

## Structure

```text
custom_addons/client_support_intervention/
├── data/  demo/  models/  report/  security/  tests/  views/
├── __init__.py
└── __manifest__.py
docs/
config/odoo.conf.example
docker-compose.yml
.env.example
LICENSE
```

## Limites et améliorations prévues

La validation client est une attestation nominative horodatée, pas une signature électronique certifiée. Le rappel d'échéance utilise une activité interne et non un courriel. Les prochaines évolutions possibles sont un portail client, des SLA configurables, des tableaux de bord, une signature tactile et une CI exécutant l'installation sur une base éphémère.

## Licence

Ce module est distribué sous LGPL-3. Le fichier [LICENSE](LICENSE) conserve le texte de licence applicable. Odoo est une dépendance externe et demeure soumis à ses propres droits d'auteur et licences.
