
# syntaxe
## les titres

Une ligne commançant par un certain nombre de `=` est considéré comme un titre. Le nombre de `=` défini la profondeur du niveau de titre (sans limite théorique)

## les sections

Une section est une zone de texte coincée entre deux titres, ou le début du document et un titre. Elle peut être associée à un titre.

## les paragraphes

Un paragraphe est une suite contigüe d'alineas, soit une zone contigue de texte séparée du reste par 2 retours à la ligne consécutifs (ie. `\n\n`).

## les alineas

Un alinéa est une simple ligne de texte, entre deux retours à la ligne. Les retours à la ligne eux même n'ayant pas d'impact sur la mise en page (ie. ils ne sont rendus que comme un simple espace, comme en html) mais ils peuvent servir à marquer la traçabilité

## les listes

Les listes à points sont introduites par le caractère `-` et les listes à numéro, par le caractère `.` suivit d'un espace

En cas de listes imbriquées, le niveau de profondeur est noté par une tabulation

## les éléments

D'une manière générale, un bloc est identifié par la syntaxe `espace.nom<contenu|attributs>`
La mention de l'espace par défaut n'est pas obligatoire, l'espace par défaut est alors `marccup`

Si l'élément est un paragraphe à lui tout seul (excepté un indicateur de traçabilité), alors l'élément est marqué de niveau paragraphe (celà à un impact pour les formules)

Si l'élément contient un signe `<`, `>` ou `|` qui n'a pas de valeur syntaxique (ie. qui est juste présent dans le corps du texte), il doit être échappé par la syntaxe %lt, %gt, %pip (_en fait, seul %gt est vraiment utile pour lever l'ambiguité, mais d'avoir les deux permets quand même un parsing amélioré_)

Une syntaxe alternative permet d'utiliser un double marqueur de début de de fin `espace.nom<<contenu|arguments>>` qui permet donc d'avoir des caractères `<` ou `>` simples, mais pas doubles

La partie argument colle à la syntaxe de oaktree, soit des champs tels que décrit ci-dessous, séparés par des espaces:

- un unique identifiant d'expression régulière : `/#[a-zA-Z][a-ZA-Z0-9_]*/`
- un ou plusieurs styles d'expression régulière : `/@[a-zA-Z][a-ZA-Z0-9_]*/`
- des champs positionnels d'expression régulière : `/{.*?}/` (_peut-être qu'il faudrait en limiter l'usage concret_)
- des champs nommés, d'expression régulière : `/[a-zA-Z][a-ZA-Z0-9_]*{.*?}/`

Le contenu des champs nommés ou positionnels ne peux pas contenir d'accolade `{` ou `}`, ces caractères doivent êtres échappés par %lbra et %rbra respectivement (_en fait, seul %rbra est vraiment utile pour lever l'ambiguité_).

## Les raccourcis

* `^<content>` devient `sup<content>`
* `_<content>` devient `sub<content>`
* `$<content>` devient `math<content>`
* `@<content>` devient `link<content>`
* `'<content>` devient `code<content>`
* `"<content>` devient `quote<content>`
* `~<content>` devient `note<content>`
* `§<content>` devient `req<content>`

### les formules de math

* Notées `$<formule>` ou `math<formule>`.
* Rendues sous leur forme _en ligne_ ou _en bloc_ suivant le contexte
* La numérotation des équations est automatique pour toutes les équations portant un label.
* On peut y ajouter des argument après un pipe `|`:
	* `#label` auquel il pourra être fait référence sous la forme `@<eqn.label>`. Le label doit être compatible de l'expression régulière `[a-zA-Z][a-ZA-Z0-9_]*`

L'élement `math<>` n'accepte aucun sous élément

### Les images et figures

* Notées `\fig<content>`.
* Rendue comme un élément flottant si l'image est _en ligne_. La numérotation des figures est automatique et une référence est insérée dans le texte.

L'élement `\fig` n'accepte aucun sous élément

### Les tables

Les lignes sont séparées par trois tirets `---`
Les colonnes sont séparées par un pipe `|`

Les champs qui commencent par `=` sont considérés comme des entêtes de table

```
table<
	= Lorem |= ipsum |= dolor ---
	sit | amet | consectetur ---
	adipiscing | elit | Nullam
|#label>
```

# le parsing

1. Les éléments raccourcis sont remplacés par leurs formes complètes
2. Les blocs de marccup sont mis de côté temporairement
3. Les sections, paragraphes, titres et alinéas sont découpés, la traçabilité est également extraite
4. Les blocs sont parsés
5. si c'est un bloc qui peut contenir une section, paragraphe ou alinéa, sont contenu est parsé à nouveau

_pour un élément, le contenu est considéré comme le `pos[0]`_

## traçabilité

Le marqueur de traçabilité est défini par l'expression régulière `§[0-9]+`
Il doit être unique sur l'ensemble du document

Les marqueurs de la traçabilité sont associé à:
- une section (le marqueur est positionné dans la ligne de titre)
- un paragraphe (le marqueur est positionné seul dans la dernière ligne)
- un alinea (le marqueur est placé en fin de ligne)

Les titres (et donc les sections) sont numérotés d'office.
Lors de l'édition, l'utilisation d'un marqueur sans identifiant numérique `§` déclenchera en post-traitement, l'attribution d'un numéro unique.

# les formules de math

Les syntaxes intéressantes:
* latex
* [asciimath](https://asciimath.org/)
* eqn/libreoffice
