# Documentation fonctionnelle

## Parcours métier

1. L'utilisateur support crée un ticket, choisit le client et décrit le besoin.
2. Le responsable affecte un consultant et ajuste priorité, catégorie et échéance.
3. Le consultant démarre le traitement, met éventuellement le ticket en attente, puis planifie une ou plusieurs interventions.
4. Chaque intervention consigne le diagnostic, les actions et le résultat. Le client peut valider nominativement le compte rendu.
5. Le consultant résout le ticket ; le responsable peut ensuite le fermer ou le rouvrir.

Un ticket urgent crée immédiatement une activité. Une tâche horaire ajoute un rappel au consultant lorsque l'échéance est dans moins de 24 heures.

## Rôles

| Rôle | Périmètre | Suppression |
|---|---|---|
| Utilisateur support | Tickets qu'il a créés ; interventions liées en lecture | Non |
| Consultant support | Tickets et interventions qui lui sont assignés | Non |
| Responsable support | Toutes les catégories, tickets et interventions | Oui |

Les rôles sont indépendants : attribuer un seul rôle métier par utilisateur évite de cumuler les domaines des règles.

