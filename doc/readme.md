

# syntaxe
## les titres

Une ligne commançant par un certain nombre de `=` est considéré comme un titre. Le nombre de `=` défini la profondeur du niveau de titre (sans limite théorique)

## les sections

Une section est une zone de texte possédant un unique titre

## les paragraphes

Un paragraphe est tout bloc de texte séparé du reste du document par 2 retours à la ligne consécutifs (ie. `\n\n`)

## les alineas

Les alinéas n'ont pas d'impact sur la mise en page (ie. ils ne sont pas rendus), mais en ont une pour la gestion de la traçabilité.

## les listes

Les listes à points sont introduites par le caractère `-` et les listes à numéro, par le caractère `.` suivit d'un espace

En cas de listes imbriquées, le niveau de profondeur est noté par une tabulation

## les éléments

D'une manière générale, un élément est identifié par la syntaxe `\espace.nom<contenu>`
La mention de l'espace par défaut n'est pas obligatoire, l'espace par défaut est alors `marccup`

Si l'élément est un paragraphe à lui tout seul (excepté un indicateur de traçabilité), alors l'élément est marqué de niveau paragraphe (celà à un impact pour les formules)

Si l'élément contient un signe `<`, `>` ou `|`, il doit être échappé par la syntaxe %lt, %gt, %pip

## Les raccourcis

* `^<content>` devient `\sup<content>`
* `_<content>` devient `\sub<content>`
* `$<content>` devient `\math<content>`
* `@<content>` -> `\link<content>`

### Les formules de math

* Notées `$<formule>` ou `\math<formule>`.
* Rendues sous leur forme _en ligne_ ou _en bloc_ suivant le contexte. La numérotation des équations est automatique.
* On peut y associer un label `$<formule#label>` auquel il pourra être fait référence sous la forme `@<eqn#label>`. Le label doit être compatible de l'expression régulière `[a-z0-9]+`

L'élement `\math` n'accepte aucun sous élément

### Les images et figures

* Notées `\fig<content>`.
* Rendue comme un élément flottant si l'image est _en ligne_. La numérotation des figures est automatique et une référence est insérée dans le texte.

L'élement `\fig` n'accepte aucun sous élément



# les formules de math

Les syntaxes intéressantes:
* latex
* [asciimath](https://asciimath.org/)
* eqn/libreoffice
