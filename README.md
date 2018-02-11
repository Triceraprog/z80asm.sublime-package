### *(EN)* Sublime Text 3 package to use `Z80` Assembly and inject the object code through `MAME`

Contains:

- Syntax highlighting for z80asm,
- Build system to use the script described in the next point,
- A script to inject code into `MAME` and run it.

Limitation:

- Only tested working on VG5000µ at now.

A sample build system follows, where the main build uses the default exec target, and the `run` variant uses the customized build target to build then run MAME using the `vgboot.lua` to inject and run the object code.

The injection and called addresses are hard-coded in the script at `$7000`. At now, you'll need to modify the `vgboot.lua` script to change this.

### *(FR)* Package Sublime Text 3 pour utiliser un assembleur `Z80` et injecter le code objet à travers `MAME`

Contient :

- Une colorisation de syntaxe pour z80asm,
- Un système de construction utilisant le script mentionné au point suivant,
- Un script qui injecte et lance un code object dans `MAME`.

Limitation :

- Ne fonctionne pour le moment qu'avec un VG-5000µ.

Un exemple de système de construction est écrit plus bas. La cible principage utilise le système `exec` par défaut afin de construire le code objet. La variante `run` utilise le système personnalisé afin de constuire le code objet puis utiliser le script `vgboot.lua` afin d'injecter et lancer le résultat.

L'injection et l'adresse de lancement sont codées en dur dans le script à `$7000`. Pour le moment, il est nécessaire de mofier le script `vgboot.lua` pour changer cette adresse.


### Sample Build System

(EN) You'll need to change `mame_path` if it's not in your default path.

(FR) Le chemin `mame_path` devra être spécifié si `MAME` n'est pas dans votre liste de chemins par défaut.


```json
{
	"selector": "source.asm.z80",
	"cmd": ["z80asm", "-b", "-v", "$file"],
	"file_patterns": ["*.asm"],
	"file_regex": "^Error at file '([^']+)' line (\\d+): ()(.+)",

	"variants": [
		{
			"target": "z80_asm",
			"name": "run",
			"mame_path": "mame",
			"script": "vgboot.lua"
		}
	]
}
```
