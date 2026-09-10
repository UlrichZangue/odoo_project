# Guide technique

## Installation et configuration

L'image `odoo:16.0` charge `custom_addons` en lecture seule. PostgreSQL et le filestore utilisent des volumes nommés. Les secrets sont lus depuis `.env`, ignoré par Git ; `.env.example` ne contient que des placeholders. `config/odoo.conf.example` documente une configuration alternative et les véritables fichiers `.conf` locaux sont ignorés.

Ordre de chargement : groupes et règles, ACL, séquences, cron, vues/actions/menus, rapport, puis données de démonstration. Les références sont produites par `ir.sequence`. Le cron `_cron_deadline_reminders` est idempotent pour une activité existante de même type et libellé.

## Vérifications statiques

```bash
python3 -m compileall -q custom_addons/client_support_intervention
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree
for path in Path('custom_addons/client_support_intervention').rglob('*.xml'):
    ElementTree.parse(path)
print('XML OK')
PY
docker compose config
```

Les tests Odoo nécessitent l'image Docker et une base PostgreSQL disponible ; voir le README.

