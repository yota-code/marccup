Le texte est divisé en :

sections: séparées par des titres ( <section></section>, les titres sont le premier descendant )
paragraphes: séparés par un double retour à la ligne ( <p></p> )
alinéas: séparés par un simple retour à la ligne ( <span></span> )
symboles: un ensemble de trucs, tels que le contenu d'un tag ( <span></span> )
mots: séparés par des espaces

Un alinéa peut éventuellement commencer par une ou plusieurs tabulations

Le symbole de marquage sera <>

Et de manière plus générale: '\tag<content>'

Si un '\tag<content>' constitue un paragraphe à lui tout seul, alors il est considéré comme tel
De même pour un alinéa

Sinon c'est un symbole

un lien interne sur une section est défini par @<document#489>

où document est le nom d'un dossier et 489 est le nom du fichier contenant la section

pour un lien vers une équation (equ) un schéma (fig) @<!equ#159>


https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl

mot::
definition du mot

## syntax

* sup (^) and sub (_) can not contain alinea break
* 

## List

List can be nested. But a list item can only contain

* either another list
* or an alinea

One can not put chapter or section as list item

## Section, Page and Document

This defines three level of object in marccup:

### Section

A section consists in a single block of text with at most one level 1 title on top.

### Page

A page consists of a combination of titles and blocks of text. Where the first title must be of level 1 and all other title levels must be consistent

### Document

A document is contained in a folder which holds a __doc__.mcp file containing only the titles.

## Highlight

When it covers only a part of an alinea :

    Curabitur molestie sapien lacus, !<ac aliquet neque blandit quis>. Vivamus eu neque quis mi ullamcorper condimentum.

    <alinea|Curabitur molestie sapien lacus, <important {1}|ac aliquet neque blandit quis>. Vivamus eu neque quis mi ullamcorper condimentum.|>

    <span>Curabitur molestie sapien lacus, <span class="mcp-important-1">ac aliquet neque blandit quis</span>. Vivamus eu neque quis mi ullamcorper condimentum.</span>

When it covers a full alinea :

    !<Curabitur molestie sapien lacus, ac aliquet neque blandit quis. Vivamus eu neque quis mi ullamcorper condimentum.>

    <alinea important{1}|Curabitur molestie sapien lacus, \important<ac aliquet neque blandit quis|1>. Vivamus eu neque quis mi ullamcorper condimentum.|>

    <span class="mcp-important-1">Curabitur molestie sapien lacus, ac aliquet neque blandit quis. Vivamus eu neque quis mi ullamcorper condimentum.</span>
