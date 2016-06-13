acid.compiler
=============

Ce module s'occupe de traduire notre AST Acid en AST Python grâce au module `ast`
de la librairie standard de Python. Ainsi, grâce à notre AST Python obtenu, nous
pouvons "compiler" notre code Acid en objet compréhensible par l'interpréteur
Python via la fonction *built-in* `compile`.

Notre classe `Compiler` est chargée de compiler notre code Acid brut en un objet
de code Python, et éventuellement de le stocker dans un fichier binaire en ROM.

Ainsi, nous pouvons exécuter plus tard un code Acid sans passer par les étapes
du *lexing*, du *parsing*, et de la traduction en AST Python.

Note: ce n'est pas de la compilation en code machine, mais plutôt en *bytecode*
de la machine virtuelle de Python. Nous ne pouvons pas transformer notre code
en exécutable (ni sous Windows, ni sous Linux/OS X) avec cette technique.
