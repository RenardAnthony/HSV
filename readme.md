# 🌀 HSV - Helicopter Stabilisation Visualisator

**HSV** est un outil visuel en temps réel conçu pour Microsoft Flight Simulator 2020 (ou tout simulateur compatible SimConnect), permettant d’aider le pilote d’un hélicoptère à maintenir une position stable au-dessus d’un point précis.

## 📸 Aperçu

*Capture d’écran à insérer ici*

---

## ✨ Fonctionnalités

- ✅ Visualisation 2D de la position par rapport à un point de référence
- ✅ Indicateur d’alignement horizontal (distance au sol)
- ✅ Indicateur d’alignement vertical (différence d’altitude)
- ✅ Cercles de distance configurables
- ✅ Tolérances personnalisables (mètres / pieds)
- ✅ Activation rapide par une touche globale (`f` par défaut)
- ✅ Interface simple avec `Tkinter`
- ✅ Fichier `settings.json` pour sauvegarder les préférences

---

## 🧰 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/tonpseudo/hsv-visualisator.git
cd hsv-visualisator
```

### 2. Installer les dépendances

Assure-toi d’avoir Python 3.10+ installé sur ta machine, puis lance :

```bash
pip install -r requirements.txt
```

### 3. Lancer l’application

```bash
python main.py
```

> ℹ️ Compatible uniquement avec Windows, car basé sur SimConnect.

---

## 📂 Arborescence du projet

```
HSV/
├── assets/
│   └── helico.png              # Icône d’hélicoptère affichée à l’écran
├── main.py                     # Script principal
├── requirements.txt            # Liste des dépendances
├── settings.json               # Généré automatiquement
└── README.md                   # Ce fichier
```

---

## ⚙️ Paramètres modifiables

Les paramètres suivants sont modifiables via l’interface graphique de l’app :

| Paramètre               | Description                                      | Valeur par défaut |
|-------------------------|--------------------------------------------------|-------------------|
| `activation_key`        | Touche d’activation du mode HSV                  | `f`               |
| `circles_meters`        | Rayons des cercles de distance (en mètres)       | `[2, 5, 10]`      |
| `altitude_range`        | Échelle verticale en pieds (± x ft)              | `40`              |
| `alignment_tolerance`   | Tolérance horizontale (m) et verticale (ft)      | `1.0` / `1.0`     |

Ces paramètres sont sauvegardés dans le fichier `settings.json`.

---

## 🛠️ Dépendances techniques

- [`SimConnect`](https://pypi.org/project/SimConnect/) (MSFS SDK Python wrapper)
- [`keyboard`](https://pypi.org/project/keyboard/) (pour la touche d’activation globale)
- [`Pillow`](https://pypi.org/project/Pillow/) (pour les images)
- `tkinter` (inclus avec Python)

---

## 📦 requirements.txt (à générer avec `pip freeze > requirements.txt`)

Exemple de contenu :

```
SimConnect==0.5.1
keyboard==0.13.5
Pillow==10.2.0
```


---

## 🧑‍💻 Auteur

Développé avec par **CherryStackStudio**

Certaines briques de code sortent de ChatGPT et MistralAI/LeChat