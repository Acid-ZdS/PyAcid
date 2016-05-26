Acid TODO-list
==============

Vous trouverez ici ce qui a été implémenté, et ce qu'il reste à coder.


## TODO

Les fonctionnalités restant à implémenter dans Acid.

- Traduction en AST Python
- Compilation à partir de l'AST Python obtenu
- Créer un algorithme pour vérifier si les variables utilisés à un endroit du
code ont bien été déclarés quelque part (pour éviter les erreurs comme NameErorr
à l'exécution comme en Python)
- *type-checker* statique ? (qui signale les erreurs à la compilation)
- Algorithme de *constant-folding*

## DONE

Les fonctionnalités déjà implémentées dans la version actuelle de Acid.

- Lexer
- Parser
