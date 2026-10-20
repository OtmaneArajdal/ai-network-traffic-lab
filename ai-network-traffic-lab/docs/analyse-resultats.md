# Analyse des résultats — Référence de trafic et écarts à investiguer

## Ce que le modèle a appris

L'ajustement sur les seize observations d'entraînement donne l'équation suivante :

**ŷ = 4,6729000151 + 1,5103001056 × x**

Pour la présentation, elle peut être arrondie à **ŷ ≈ 4,67 + 1,51x**. Les prédictions et les métriques ci-dessous restent calculées avec les coefficients non arrondis.

La pente signifie qu'une augmentation d'un utilisateur est associée à environ 1,51 Mbps supplémentaires dans la prédiction du modèle. Cette valeur décrit la relation présente dans les données synthétiques. Elle ne permet pas d'affirmer que chaque utilisateur consomme toujours ce débit ni que le nombre d'utilisateurs est la seule cause des variations de trafic.

L'intercept, proche de 4,67 Mbps, est la valeur mathématique obtenue lorsque le nombre d'utilisateurs vaut zéro. Comme aucune observation du jeu ne correspond à zéro utilisateur, il ne peut pas être présenté comme une mesure de trafic de fond. Son rôle est d'abord de positionner la droite ajustée.

## Prédictions sur le jeu de test

Les résultats obtenus sur les quatre observations gardées à l'écart de l'entraînement sont les suivants. Le résidu suit la convention **trafic observé − trafic prédit**.

| Utilisateurs | Trafic du jeu (Mbps) | Trafic prédit (Mbps) | Résidu (Mbps) |
|---:|---:|---:|---:|
| 10 | 20 | 19,775901 | +0,224099 |
| 95 | 149 | 148,151410 | +0,848590 |
| 85 | 133 | 133,048409 | −0,048409 |
| 15 | 27 | 27,327402 | −0,327402 |

L'observation à **95 utilisateurs** possède le plus grand résidu absolu du test, soit environ **0,8486 Mbps**. Le modèle sous-estime alors légèrement le trafic : il prévoit 148,1514 Mbps pour une valeur de 149 Mbps. À l'inverse, à 15 et 85 utilisateurs, il surestime le trafic, ce qui explique les résidus négatifs.

Cette lecture individuelle complète la moyenne des erreurs. Elle permet de repérer le point le moins bien prédit, mais quatre résidus sont insuffisants pour caractériser une distribution d'erreurs en conditions réelles. Je ne conclus donc pas à une absence systématique de biais ou à une stabilité du modèle sur tous les niveaux de charge.

## Métriques et portée de la performance

| Indicateur | Valeur obtenue | Lecture dans ce lab |
|---|---:|---|
| MAE | 0,3621248680 Mbps | Écart absolu moyen sur les quatre points de test |
| MSE | 0,2199651202 (Mbps)² | Moyenne des écarts au carré |
| R² | 0,9999369671 | Très faible erreur quadratique par rapport à la référence constante sur ce test |

La MAE indique une erreur moyenne d'environ 0,36 Mbps sur ce découpage. La MSE reste faible, ce qui est cohérent avec les petits résidus du tableau. Les unités sont différentes : la MSE n'est pas directement un débit moyen. [Guide officiel d'évaluation des modèles](https://scikit-learn.org/stable/modules/model_evaluation.html)

R² est très proche de 1, mais ce chiffre doit être lu dans son contexte. Il ne mesure ni la probabilité de cyberattaque ni le pourcentage d'incidents correctement détectés. Il compare les prédictions du modèle aux valeurs de test, relativement à leur moyenne. [Documentation officielle de `r2_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)

Le résultat élevé s'explique notamment par la construction du jeu : les vingt observations suivent déjà une relation presque linéaire, avec peu de dispersion. Le test ne contient que quatre points, dont les trafics s'étendent de 20 à 149 Mbps. Une erreur absolue faible par rapport à cette dispersion conduit ici à un R² très élevé. Cela montre que le modèle reproduit bien ce cas pédagogique, sans démontrer sa robustesse sur de vrais flux réseau.

La séparation entraînement/test reste utile, mais sa petite taille limite la portée de l'évaluation. Deux valeurs de test, 10 et 15 utilisateurs, sont inférieures au minimum de l'entraînement, égal à 20. Elles constituent donc déjà de légères extrapolations par rapport aux données ayant servi à ajuster la droite. Leurs erreurs faibles dans cet exemple ne garantissent pas que toute extrapolation sera fiable.

## Scénario source : 220 Mbps pour 110 utilisateurs

À 110 utilisateurs, le trafic attendu vaut **170,8059116272 Mbps**, soit environ 170,81 Mbps. Cette entrée dépasse le maximum du jeu, qui est de 105 utilisateurs : il s'agit d'une légère extrapolation. Il faut la signaler plutôt que de présenter la prévision comme une valeur vérifiée dans le domaine observé.

Le sujet fixe ensuite un trafic simulé de 220 Mbps. Le résidu est :

**e = 220 − 170,8059116272 = +49,1940883728 Mbps**

La valeur absolue dépasse le seuil pédagogique de 40 Mbps. La règle demande donc une investigation. Elle indique que le trafic simulé est sensiblement supérieur à la référence donnée par le modèle ; elle n'identifie pas l'origine de cet écart.

Une mise à jour, une sauvegarde, un transfert volumineux, un changement d'application ou une erreur de mesure peuvent également produire une hausse de trafic. L'existence d'un écart ne suffit donc pas à attribuer un comportement malveillant à un utilisateur ou à un flux.

## Extension de la reprise du 20 octobre 2026

Les valeurs 160, 180 et 120 Mbps ont été ajoutées pour étudier le comportement de la règle. Elles ne figurent pas comme scénarios dans le sujet initial. Le cas à 220 Mbps est conservé pour permettre la comparaison. Les quatre lignes utilisent 110 utilisateurs, la même prévision de 170,8059 Mbps et le même seuil strict **|e| > 40 Mbps**.

| Trafic simulé (Mbps) | Résidu (Mbps) | Valeur absolue (Mbps) | Décision de la règle |
|---:|---:|---:|---|
| 160 | −10,805912 | 10,805912 | Pas de signalement par cette règle |
| 180 | +9,194088 | 9,194088 | Pas de signalement par cette règle |
| 220 | +49,194088 | 49,194088 | Observation à investiguer |
| 120 | −50,805912 | 50,805912 | Observation à investiguer |

L'exemple à 120 Mbps est utile : une baisse importante déclenche aussi la règle, car elle utilise la valeur absolue du résidu. Une baisse pourrait correspondre à une interruption de service, à une variation légitime d'activité ou à un problème de collecte. Le programme ne distingue pas ces causes.

Pour cette prévision précise, les valeurs comprises entre environ **130,81 et 210,81 Mbps**, bornes incluses avant arrondi, ne dépassent pas le seuil. Cette plage est seulement la conséquence de l'addition et de la soustraction de 40 Mbps ; ce n'est pas un intervalle de confiance statistique. Une valeur non signalée n'est pas pour autant démontrée comme sûre.

## Apport en cybersécurité et limites

L'intérêt de la régression linéaire est ici de fournir une référence explicite. Au lieu de considérer un débit isolé, je peux le comparer à une estimation dépendant du nombre d'utilisateurs. Le résidu fournit une mesure d'écart et la droite reste facile à expliquer. Cette transparence est utile pour relier un résultat numérique à une décision d'investigation.

Les limites restent importantes. Le jeu est petit et synthétique ; il ne contient ni horodatage, ni protocole, ni application, ni volume de trafic par utilisateur. Le seuil est arbitraire et aucune étiquette ne permet de distinguer une activité légitime d'une attaque. Il n'est donc pas possible de calculer un rappel d'attaques, une précision de détection ou un taux de faux positifs validé. Une attaque produisant peu d'écart peut aussi ne pas être signalée.

Avant de conclure à un incident, il faudrait examiner les journaux, les adresses et destinations, les protocoles, les authentifications et les tâches planifiées. Le contexte horaire doit être comparé aux habitudes du système : une activité de nuit n'est pas suspecte par principe.

## Apprentissages et améliorations possibles

Ce lab m'a surtout permis de relier les étapes de modélisation à leur interprétation. Le modèle apprend une tendance ; la métrique décrit une erreur ; la règle de seuil transforme un écart en signalement ; l'analyste doit encore en rechercher la cause. Ces niveaux ne doivent pas être confondus.

Pour poursuivre le travail, je commencerais par collecter davantage de données horodatées et par définir une fenêtre de mesure stable. Une séparation chronologique permettrait d'évaluer le modèle sur une période postérieure à l'entraînement. J'ajouterais ensuite des variables utiles, comme le type d'application, les débits entrants et sortants, l'heure et les tâches planifiées. Le seuil serait calibré sur un ensemble de validation séparé, puis évalué sur des événements documentés, en tenant compte du coût des alertes inutiles et des incidents manqués.

L'objectif d'une telle extension serait d'améliorer la validité de l'évaluation avant de complexifier le modèle. Le score presque parfait de cet exercice reste un résultat de reproduction sur des données pédagogiques ; le principal acquis est une méthode de raisonnement vérifiable et prudente.
