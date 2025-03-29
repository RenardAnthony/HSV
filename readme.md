
# 🌀 HSV - Helicopter Stabilisation Visualisator

**HSV** est un outil visuel en temps réel conçu pour **Microsoft Flight Simulator 2024** (ou tout simulateur compatible SimConnect), permettant d’aider le pilote d’un hélicoptère à maintenir une position stable au-dessus d’un point précis.

---

## 📦 Version exécutable (`.exe`)

> Tu veux tester rapidement sans rien installer ?  
Télécharge simplement la version `main.exe` précompilée dans le dossier `build/` !

✅ Aucun besoin d’installer Python  
✅ Dépendances incluses  
✅ Il suffit de double-cliquer !  
❌ Fonctionne uniquement sur **Windows**

---

## 🧰 Installation développeur (version complète)

Tu veux lire, modifier ou contribuer au code ? Voici comment installer le projet sur ta machine.

### 1. Cloner le projet

```bash
git clone https://github.com/tonpseudo/hsv-visualisator.git
cd hsv-visualisator
```

### 2. Créer un environnement virtuel (optionnel mais recommandé)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
python main.py
```

> ℹ️ Fonctionne uniquement sur **Windows** (SimConnect est une API native MSFS).

---

## ✨ Fonctionnalités

- ✅ Visualisation 2D de la position par rapport à un point de référence
- ✅ Indicateur d’alignement horizontal (distance au sol)
- ✅ Indicateur d’alignement vertical (différence d’altitude)
- ✅ Cercles de distance configurables
- ✅ Tolérances personnalisables (mètres / pieds)
- ✅ Lignes seuils pour l'altitude
- ✅ Activation rapide par une touche globale (`f` par défaut)
- ✅ Interface Tkinter
- ✅ Fichier `settings.json` pour sauvegarder les préférences

---

## 📂 Arborescence du projet

```
HSV/
├── assets/
│   └── helico.png              # Icône hélicoptère
├── build/
│   └── main.exe                # (optionnel) Fichier exécutable prêt à l’emploi
├── main.py                     # Script principal
├── requirements.txt            # Dépendances
├── settings.json               # Généré automatiquement
├── README.md                   # Ce fichier
└── builder.bat                 # Crée automatiquement t'on .exe
```

---

## ⚙️ Paramètres modifiables

| Paramètre               | Description                                      | Valeur par défaut |
|-------------------------|--------------------------------------------------|-------------------|
| `activation_key`        | Touche d’activation du mode HSV                  | `f`               |
| `circles_meters`        | Rayons des cercles de distance (en mètres)       | `[2, 5, 10]`      |
| `altitude_range`        | Échelle verticale en pieds (± x ft)              | `40`              |
| `alignment_tolerance`   | Tolérance horizontale (m) et verticale (ft)      | `1.0` / `1.0`     |

Ces paramètres sont enregistrés dans `settings.json` après modification via l'interface.

---

## 🛠️ Dépendances

- [`SimConnect`](https://pypi.org/project/SimConnect/) (wrapper Python MSFS)
- [`keyboard`](https://pypi.org/project/keyboard/) (touche d’activation globale)
- [`Pillow`](https://pypi.org/project/Pillow/) (gestion d’image)
- `tkinter` (inclus avec Python)

---

## 🧊 Geler les dépendances

Si tu fais des modifs, tu peux mettre à jour `requirements.txt` avec :

```bash
pip freeze > requirements.txt
```

---

## 🧑‍💻 Auteur

Développé avec par **MrFoxit** de **CherryStackStudio**

Certaines briques de code viennent de ChatGPT et LeChat (MistralAI)
