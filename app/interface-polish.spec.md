---
title: 'Créer une interface complète pour l’estimateur immobilier'
type: 'feature'
created: '2026-10-08'
status: 'in-review'
baseline_commit: 'NO_VCS'
context: []
---

<frozen-after-approval reason="human-approved expanded intent">

## Intent

**Problem:** Le projet expose aujourd’hui un estimateur isolé, sans navigation ni pages qui donnent l’impression d’une application immobilière cohérente et aboutie.

**Approach:** Construire une petite application Flask en français avec un accueil, un parcours d’estimation, un résultat détaillé et une page « À propos », tous réunis par une navigation et un design responsive professionnels. Préserver le modèle et le contrat de l’API de prédiction; ne pas ajouter d’historique persistant.

## Boundaries & Constraints

**Always:** Garder Flask, l’URL d’accueil `/`, la route JSON `/predict` et les mêmes champs envoyés au modèle. Ajouter des pages cohérentes pour `/estimer` et `/a-propos`; assurer navigation au clavier, libellés visibles, messages accessibles et adaptation mobile/ordinateur. Le résultat ne doit présenter que les valeurs réellement calculées et les informations saisies.

**Ask First:** Toute nouvelle fonctionnalité métier, conservation ou historique des estimations, ou modification de la logique de prédiction.

**Never:** Ajouter un framework front-end, des dépendances ou des ressources externes; ajouter une connexion utilisateur, une base de données ou un historique; modifier les modèles, leurs données ou les calculs de prédiction.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|----------------------------|----------------|
| Navigation | Ouvrir l’accueil, l’estimation ou « À propos » puis suivre les liens | Chaque page existe, partage le même habillage et dispose d’une navigation fonctionnelle | Une page inexistante reste gérée par Flask |
| Estimation valide | Formulaire complet, appartement ou maison | Résultat détaillé dans le parcours d’estimation avec prix estimé et prix au m² | Bouton et état de chargement rétablis |
| Champs incomplets | Surface ou pièces manquantes | Le formulaire indique les champs à compléter et ne lance pas la requête | Message d’erreur compréhensible, associé au formulaire |
| Réponse serveur invalide | Erreur HTTP ou réponse sans résultat exploitable | Aucun faux résultat n’est affiché | Message d’erreur visible; formulaire réactivé |
| Type maison | Sélection de « Maison » puis « Appartement » | Le champ de terrain devient visible puis est masqué | N/A |

</frozen-after-approval>

## Code Map

- `app\app.py` -- routes Flask et prédiction existantes à préserver et à relier aux pages.
- `app\templates\` -- gabarits partagés et pages d’accueil, d’estimation et « À propos ».
- `app\static\style.css` -- styles responsives partagés.

## Tasks & Acceptance

**Execution:**
- [x] `app\app.py` -- Rendre l’accueil, l’estimation et la page « À propos »; conserver `/predict` comme API JSON inchangée et transmettre les erreurs HTTP correctement.
- [x] `app\templates\base.html` -- Créer le cadre commun avec navigation responsive, liens actifs et structure accessible.
- [x] `app\templates\index.html`, `app\templates\estimate.html`, `app\templates\about.html` -- Construire l’accueil, le formulaire/résultat détaillé et les explications sur le périmètre des estimations.
- [x] `app\static\style.css` -- Fournir l’identité visuelle cohérente, responsive, avec états de focus et de formulaire visibles.

**Acceptance Criteria:**
- Given un visiteur, when il ouvre l’accueil et utilise les liens principaux, then il peut accéder aux pages d’estimation et « À propos » dans une interface cohérente et responsive.
- Given le choix d’un type de bien, when « Maison » est sélectionné puis « Appartement », then le champ de terrain s’affiche puis se masque comme avant.
- Given une saisie valide, when l’estimation est demandée, then `/predict` reçoit le même contrat de données et le parcours affiche prix total, prix au m² et caractéristiques soumises, sans inventer d’indicateur de confiance.
- Given une erreur de validation ou de requête, when elle survient, then un message visible et compréhensible remplace l’alerte ou le silence, sans laisser le bouton bloqué.
- Given une estimation affichée, when le visiteur consulte « À propos », then la page explique clairement que les montants sont des estimations et quelles informations alimentent le calcul.

## Spec Change Log

## Design Notes

Utiliser une palette sobre et chaleureuse, une hiérarchie typographique nette, des espacements réguliers et des contrôles avec états de focus visibles. L’accueil sert de point d’entrée avec un appel à l’action vers l’estimation. La page d’estimation combine formulaire et panneau de résultat détaillé; la page « À propos » explique honnêtement le fonctionnement sans promettre la précision ni inventer de nouvelles métriques. Rendre les erreurs compréhensibles sans dépendre uniquement de la couleur.

## Verification

**Commands:**
- `python -m py_compile .\app\app.py` -- expected: compilation réussie.
- Vérification des pages et de la navigation via le client de test Flask ou le navigateur -- expected: HTTP 200 sur `/`, `/estimer`, `/a-propos`; envoi de l’estimation toujours compatible avec `/predict`.

**Manual checks (if no CLI):**
- Vérifier visuellement la navigation et chaque page en largeur étroite et large, le changement de type, la validation, l’attente, le résultat et les erreurs de requête.
