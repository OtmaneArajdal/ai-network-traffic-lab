# Méthodologie — Régression linéaire appliquée au trafic réseau

## Objectif et périmètre

L'objectif de ce travail est de construire une estimation simple du trafic réseau à partir du nombre d'utilisateurs connectés, puis d'étudier les écarts entre cette estimation et une observation. J'ai repris le protocole du sujet pour comprendre chaque étape : préparation des données, séparation entraînement/test, ajustement de la droite, évaluation et interprétation des résidus. La partie cybersécurité intervient ensuite, lorsqu'un écart suffisamment important est considéré comme un motif d'investigation.

Cette démarche constitue une démonstration pédagogique. Elle ne repose ni sur une capture de trafic réel ni sur un jeu d'attaques étiquetées. Le résultat attendu est une référence de trafic et une règle de signalement compréhensibles, pas un système de détection d'intrusion validé en production.

## Données utilisées

Le jeu reprend exactement les vingt couples du sujet. La variable d'entrée est `utilisateurs`, un nombre de personnes connectées. La variable cible est `trafic`, exprimée en Mbps. Le nombre d'utilisateurs va de 10 à 105, par pas de 5 ; le trafic associé va de 20 à 165 Mbps. Les valeurs sont synthétiques et présentent une relation presque linéaire.

Le script lit le CSV fourni, tandis que le notebook intègre les mêmes vingt couples afin de fonctionner seul dans Colab. La vérification de préparation compare ces deux jeux, contrôle les vingt observations numériques et leur absence de valeurs manquantes. La cible est nommée `trafic_mbps` dans les fichiers du dépôt. Aucune observation n'est ajoutée au jeu d'apprentissage pour simuler une attaque. Les scénarios d'investigation restent séparés des données d'entraînement et du test.

Le sujet ne précise pas de fenêtre de mesure, de date, de type d'application ou de sens de circulation du trafic. Ces informations ne sont donc pas inventées dans l'analyse. Le mot « trafic » désigne ici uniquement la grandeur synthétique exprimée en Mbps dans le sujet.

## Exploration et préparation des variables

Un nuage de points permet d'examiner la relation entre le nombre d'utilisateurs et le trafic. Les points suivent une tendance croissante proche d'une droite, ce qui rend la régression linéaire cohérente pour cet exercice. Cette observation justifie l'essai d'un modèle simple ; elle ne suffit pas à établir une relation causale dans un réseau réel.

La matrice `X` contient une seule colonne, `utilisateurs`, alors que `y` contient le trafic à prédire. Cette distinction permet de séparer les informations fournies au modèle de la grandeur qu'il doit estimer. Le jeu complet sert à explorer la relation, mais seul le sous-ensemble d'entraînement est utilisé pour ajuster les paramètres.

## Séparation entraînement/test

La séparation suit les paramètres du sujet : `test_size=0.20` et `random_state=42`. Elle donne seize observations d'entraînement et quatre observations de test. L'entier fixé rend le tirage reproductible pour une même configuration de données et d'outils. La fonction mélange les observations par défaut ; il ne s'agit pas d'une séparation chronologique. [Documentation officielle de `train_test_split`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)

Les quatre valeurs d'entrée retenues pour le test sont 10, 95, 85 et 15 utilisateurs, dans cet ordre. Elles sont gardées à l'écart de l'ajustement. Le modèle est ensuite évalué en comparant ses prédictions aux valeurs de trafic correspondantes. Cette séparation fournit une mesure hors entraînement ; elle n'empêche pas à elle seule le surapprentissage et ne garantit pas que quatre observations représentent la diversité d'un réseau réel.

## Ajustement du modèle

Le modèle est une régression linéaire simple de la forme :

**ŷ = β₀ + β₁ × x**

`x` représente le nombre d'utilisateurs et `ŷ` le trafic estimé en Mbps. `β₀` est l'intercept, tandis que `β₁` indique la variation de la prédiction pour une unité supplémentaire de `x`. L'estimateur `LinearRegression` ajuste les coefficients par moindres carrés : il recherche les paramètres qui minimisent la somme des carrés des résidus sur l'entraînement. [Documentation officielle de `LinearRegression`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

L'intercept est conservé. Les paramètres sont calculés sur les seize observations d'entraînement, puis utilisés sans réajustement pour le test et les scénarios complémentaires. Les calculs gardent leur précision numérique ; l'arrondi à deux décimales est réservé à la lecture du rapport. Cette distinction évite de modifier légèrement les métriques en réutilisant une équation déjà arrondie.

## Résidus et critères d'évaluation

Pour chaque observation de test, le résidu est calculé par **e = y − ŷ**. Un résidu positif correspond à un trafic supérieur à la prévision, et un résidu négatif à un trafic inférieur. L'observation la plus éloignée de la droite est identifiée à partir de la plus grande valeur absolue du résidu, et pas seulement du résidu positif le plus élevé.

Trois indicateurs sont calculés sur les quatre observations de test : la MAE, moyenne des erreurs absolues, la MSE, moyenne des erreurs au carré, et R². La MAE s'exprime en Mbps ; la MSE en (Mbps)². Le carré rend la MSE davantage sensible aux erreurs importantes. [Guide officiel d'évaluation des modèles de scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html)

R² compare la somme des erreurs quadratiques à celle d'une prédiction constante fondée sur la moyenne des valeurs évaluées. Sa valeur optimale est 1 ; une valeur de 0 correspond à cette référence constante, et des valeurs négatives sont possibles. Il ne s'agit pas d'un pourcentage d'attaques correctement détectées. [Documentation officielle de `r2_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)

Les tableaux conservent les observations, les prédictions et les résidus associés. Les graphiques distinguent les points d'entraînement et de test et montrent la droite ajustée. Cette présentation permet de vérifier ce que le modèle a appris et ce qui a réellement servi à son évaluation.

## Scénario d'investigation et extension

Le scénario du sujet utilise 110 utilisateurs et un trafic observé simulé de 220 Mbps. Le modèle estime d'abord le trafic attendu ; la règle déclenche ensuite un signalement si **|e| > 40 Mbps**. Le seuil de 40 Mbps est repris comme une constante pédagogique. Il n'est ni appris par le modèle ni calibré sur des incidents connus. Un écart exactement égal à 40 Mbps ne déclenche pas le signalement.

Pour rendre l'effet de cette règle plus concret, la reprise du 20 octobre 2026 compare quatre valeurs simulées à 110 utilisateurs : 160, 180, 220 et 120 Mbps. La valeur 220 appartient au scénario source ; les autres valeurs constituent une extension de cette reprise. Elles ne doivent pas être présentées comme des observations fournies par le sujet ou recueillies sur un réseau.

Les mêmes coefficients sont utilisés pour les quatre cas. Seule la valeur du trafic simulé change. Ce choix permet d'isoler le lien entre l'observation, le signe du résidu et la décision de la règle, sans modifier le modèle ou son seuil après avoir vu les résultats.

## Organisation de la reproduction

Le protocole se décline en un notebook lisible cellule par cellule et un script Python permettant une exécution complète. Les sorties comprennent les données et résultats en CSV, les coefficients et métriques en JSON, ainsi que les graphiques. Le contrôle de cohérence consiste à retrouver le même découpage, les mêmes paramètres et les mêmes métriques dans les deux parcours, à la précision numérique près.

Cette organisation facilite la reprise du travail et son partage sur GitHub. Elle distingue les données synthétiques, les résultats calculés et l'interprétation. La préparation du dépôt et la réexécution datent du 20 octobre 2026. Les versions effectivement utilisées figurent dans `results/summary.json` ; elles ne décrivent pas l’environnement de la session Colab visible dans les captures du support.
