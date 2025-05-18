# 📌 Description Complète du Modèle JSON

## 📖 **Sommaire**
1️⃣ [Présentation Générale du Modèle](#1️⃣-pr%C3%A9sentation-g%C3%A9n%C3%A9rale-du-mod%C3%A8le)
2️⃣ [Structure Générale du JSON](#2️⃣-structure-g%C3%A9n%C3%A9rale-du-json)
3️⃣ [Définition des Tables et Relations](#3️⃣-d%C3%A9finition-des-tables-et-relations)
4️⃣ [Définition des Champs](#4️⃣-d%C3%A9finition-des-champs)
5️⃣ [Options et Paramètres des Champs](#5️⃣-options-et-param%C3%A8tres-des-champs)
6️⃣ [Configuration des Étapes et Navigation](#6️⃣-configuration-des-%C3%A9tapes-et-navigation)
7️⃣ [Gestion des Affichages Dynamiques](#7️⃣-gestion-des-affichages-dynamiques)
8️⃣ [Gestion des Fichiers et Téléchargements](#8️⃣-gestion-des-fichiers-et-t%C3%A9l%C3%A9chargements)
9️⃣ [Boutons et Actions](#9️⃣-boutons-et-actions)
🔟 [Exemples Complets](#🔟-exemples-complets)


## **1️⃣ Présentation Générale du Modèle**

Ce document décrit de manière détaillée le **modèle JSON** utilisé pour générer **les formulaires et les tableaux dynamiques** de manière générique et réutilisable.

Le modèle permet de :
- **Définir des formulaires** à une ou plusieurs étapes.
- **Gérer dynamiquement les champs et leurs paramètres**.
- **Personnaliser l'affichage des tableaux** (plat, expansible, avec filtres).
- **Configurer la navigation entre les étapes** (transitions conditionnelles).
- **Prendre en charge les fichiers et les téléchargements**.
- **Gérer les boutons d'action et de transition entre étapes**.

Le modèle JSON est structuré de manière **générique et flexible** afin de s’adapter à divers besoins métier.

---

## **2️⃣ Structure Générale du JSON**
Le modèle JSON est structuré comme suit :
```json
{
    "etape": {
        "tableMaster": {},
        "fields": {},
        "tableSecondaire": {},
        "next_step": {},
        "buttons": {}
    }
}
```

- **`tableMaster`** : Définit la table principale et ses règles de filtrage.
- **`fields`** : Contient la définition de tous les champs du formulaire.
- **`tableSecondaire`** : Définit une table secondaire si nécessaire.
- **`next_step`** : Configure la transition vers l’étape suivante.
- **`buttons`** : Définit les actions et boutons pour les étapes et les tableaux.

---

## **4️⃣ Définition des Champs**
Chaque champ est défini avec ses propriétés spécifiques :
```json
"fields": {
    "username": {
        "label": "Nom d'utilisateur",
        "form": { "type": "text", "readonly": true, "source": "session_state.user.user_name" }
    },
    "password": {
        "label": "Mot de passe",
        "form": { "type": "password" }
    },
    "email": {
        "label": "Email",
        "form": { "type": "email", "placeholder": "Entrez votre email" }
    },
    "description": {
        "label": "Description",
        "form": { "type": "textarea" }
    }
}
```

---

## **5️⃣ Options et Paramètres des Champs**

Les champs du formulaire se décrivent maintenant de manière plus granulaire:

| Propriété        | Description                                                                                                     |
|------------------|-----------------------------------------------------------------------------------------------------------------|
| type             | Type de champ (text, textarea, mail, password, number, date, file, auto, select, hidden, boolean…)              |
| source           | Contenu ou table à requêter (suivant source-type). Pour "sgbd", doit être un objet { "table":"...", "field-view":"...", "field-record":"...", "where":{}} |
| source-type      | Indique où prendre la valeur (enum / sgbd / single / session_var / now). "now" n’est compatible qu’avec date/auto. |
| where            | Dictionnaire de conditions pour filtrer les données (ex. { "status": "active" }). Applicable seulement à sgbd   |
| placeholder      | Valeur affichée en fond de champ lorsqu’aucune donnée n’est saisie                                              |
| label_visibility | Contrôle l’affichage du label (ex. "visible", "collapsed", "hidden")                                            |
| readonly         | Rend un champ non modifiable                                                                                   |
**Exemple JSON :**
```json
"upd_date": {
    "label": "Dernière Mise à Jour",
    "form": { "type": "auto", "source": "now" }
},
"created_by": {
    "label": "Créé par",
    "form": { "type": "auto", "source": "session_state.user.userId" }
}
```

### Détail sur "source-type":
• "enum" : liste de valeurs statiques. Applicable surtout aux champs "select".  
• "sgbd" : récupère les valeurs depuis la base (via "table", "field-view", "field-record", "where").  
• "single" : champ redondant contenant une chaîne de caractères unique (pas de liste).  
• "session_var" : la valeur (ou liste) est extraite de st.session_state.  
• "now" : insère la date/heure actuelle (uniquement pour "date" ou "auto").  

### Exemple JSON pour un champ "select" (enum):
```json
"prd_or_cmp": {
  "security-key": "jN4k7mPq2xR5",
  "label": "Article type",
  "form": {
    "type": "select",
    "source-type": "enum",
    "source": ["Product", "Component"],
    "placeholder": "Choisir un article",
    "label_visibility": "visible"
  }
}
```

### Exemple JSON pour un champ "select" (sgbd):
```json
"product_family": {
  "security-key": "xK9m2pQn4vL8",
  "label": "Product family",
  "form": {
    "type": "select",
    "source-type": "sgbd",
    "source": {
      "table": "ref_product_families",
      "field-view": "name",
      "field-record": "id",
      "where": { "active": true }
    },
    "placeholder": "Famille de produits",
    "label_visibility": "visible"
  }
}
```

### Compatibilité de "source-type" avec "type":
• "enum" → s’applique surtout à "select" (parfois "text" si on gère une valeur unique).  
• "sgbd" → utilisable pour "select", "auto", "text" (mais souvent "select").  
• "single" → compatibilité large (text, textarea…).  
• "session_var" → compatibilité large, y compris lists pour "select".  
• "now" → uniquement "date" ou "auto".  

### Tableau récapitulatif des types de champs
| Type       | Description                                                                                        |
|------------|----------------------------------------------------------------------------------------------------|
| text       | Champ de saisie d’une seule ligne (texte simple)                                                  |
| textarea   | Zone de texte multi-lignes                                                                        |
| email      | Champ pour la saisie d'adresses e-mail                                                            |
| password   | Champ de saisie masquée (mot de passe)                                                            |
| number     | Champ numérique éventuellement contrôlé par min/max                                              |
| date       | Sélection de date                                                                                 |
| file       | Téléversement de fichier (définit un dossier, éventuellement une URL de base)                     |
| auto       | Champ qui se remplit automatiquement (ex. date courante via "now", ou session_var)               |
| select     | Liste déroulante (valeurs statiques "enum" ou requête sgbd)                                       |
| hidden     | Champ masqué aux utilisateurs                                                                     |
| boolean    | Champ case à cocher pour des valeurs vrai/faux                                                    |

---

## Focus sur : la tableMaster et la tableSecondaire
- **tableMaster** : Indique la table principale à utiliser pour récupérer ou insérer les données de l’étape. Peut comprendre un "where" pour filtrer ces données.
- **tableSecondaire** : Permet d’afficher et de gérer des enregistrements liés (relation 1-N). Indique notamment la table à joindre, le champ de liaison et les champs affichés/édités.

## **6️⃣ Configuration des Étapes et Navigation**
### **🔹 Définition des Étapes**
Chaque étape est définie par un identifiant unique et un ensemble de règles permettant de déterminer la transition vers l’étape suivante.

**Exemple JSON :**
```json
"next_step": {
    "step": { "value": 2, "session_var": "step" },
    "entity_id": { "value": "id", "session_var": "entity_id" },
    "color": { "value": "color", "session_var": "color" },
    "{other params}" : {"value": "xxxx", "session_var": "xxxxx"},
    "next-page": "{nom_de_la_page}",
     "step_final": false // soit c'ets la dernière étape, soit on continue
}
```

### **🔹 Gestion des Transitions**
Les transitions peuvent être conditionnées à des critères spécifiques, tels que :
- Un statut (`status`)
- Une validation (`validated: true`)
- Un seuil atteint (`score > 80`)



---

## **6.1 Évolution des modèles JSON (saf_v2 et cus_v2)**
Les nouveaux fichiers saf_v2 et cus_v2 intègrent désormais :
- Une structure "Qualify" et une éventuelle "Priorization" pour séparer les étapes.
- Des champs additionnels (exemple : "detection_date", "sf_link", etc.) afin de couvrir des besoins spécifiques (URL, date).
- La configuration d’un "tableSecondaire" pour gérer des données liées (ex. "non_conformities" dans saf_v2).
- Le paramètre "tableMaster" permettant de définir la table et le where associé (pour filtrer les enregistrements par statut et type).

Ces ajouts suivent la logique générale du système et se déclinent dans le JSON avec les propriétés "source", "source-type", "fields", "next_step", etc.

---

## **7️⃣ Gestion des Affichages Dynamiques**
### **🔹 Types d’Affichage des Données**
| Mode | Description |
|------|------------|
| `table` | nom de la table secondaire |
| `kabel` | Affichage du nom de la table |
| `table` | Affichage à plat sous forme de tableau |
| `expander` | Affichage en accordéon pour masquer/développer des sections |
| `readonly_value` | Affichage d’une valeur fixe dans un champ grisé |
| `count_records` | Affichage du nombre d'enrtegistrement dant la barre de l'expander|

**Exemple d'affichage conditionnel via `expander` :**
```json
"tableSecondaire": {
    "table": "table_secondaire",
    "label" : "Table Secondaire",
    "relation": "principal_id",
    "expander": true,
    "count_records": true,
    "fields": {
        "data1": { "label": "Data 1", "form": { "type": "text" } },
        "data2": { "label": "Data 2", "form": { "type": "text" } }
    }
}
```

## **8️⃣ Gestion des Fichiers et Téléchargements**
### **🔹 Définition des Champs de Type Fichier**
Les fichiers peuvent être téléchargés et stockés dans un dossier spécifique avec une URL d'accès si nécessaire.

**Exemple JSON :**
```json
"file_upload": {
    "label": "Téléverser un fichier",
    "form": {
        "type": "file",
        "destination_folder": "uploads/documents",
        "base_url": "https://cdn.example.com/files/"
    }
}
```

| Option | Description |
|--------|-------------|
| `destination_folder` | Dossier où le fichier sera stocké |
| `base_url` | URL de base pour accéder aux fichiers téléchargés. - Optionnelle |

---

## **9️⃣ Boutons et Actions**
### **🔹 Définition des Boutons dans les Formulaires**
Certains boutons peuvent être définis pour soumettre un formulaire ou passer à l'étape suivante.

**Exemple JSON :**
```json
"form-buttons": {
    "label": "Envoyer",
    "form_submit": { "type": "submit" }
}
```

| Clé JSON | Description |
|----------|------------|
| `form_submit` | Bouton d'envoi du formulaire |
| `label` | titre du bouton |
| `form_submit` | Element de definition du type de bouton |

---

## **Security Keys**
Les "security-keys" sont des identifiants uniques générés pour chaque champ du modèle JSON, permettant de :
- Masquer le nom réel des champs dans le front-end
- Éviter l'exposition de la structure de la base de données
- Sécuriser les formulaires contre les manipulations non autorisées

### Génération des Security Keys
Les clés sont générées automatiquement via un algorithme qui :
1. Prend en compte le chemin complet du champ (ex: ["Qualify", "IncidentsAndQualifications", "prd_or_cmp"])
2. Crée un hash SHA-256 de ce chemin
3. Encode en base64 et prend les 12 premiers caractères

### Exemple dans le JSON
```json
"prd_or_cmp": {
    "security-key": "jN4k7mPq2xR5",  // Clé unique générée
    "label": "Article type",
    "form": {
        "type": "select",
        "source-type": "enum",
        "source": ["Product", "Component"]
    }
}
```

### Utilisation
- Les security-keys sont utilisées comme identifiants uniques dans les composants Streamlit (ex: st.text_input(key=security_key))
- Elles permettent d'éviter les collisions entre les champs de différents formulaires
- Elles masquent la structure réelle des tables aux utilisateurs finaux

---

## **🔟 Exemples Complets**
### **Exemple 1 : Formulaire Simple avec Validation**
```json
{
    "fields": {
        "username": { "type": "text", "required": true },
        "email": { "type": "email", "placeholder": "Entrez votre email" }
    },
    "buttons": {
        "form_submit": { "label": "Envoyer", "type": "submit" }
    }
}
```

### **Exemple 2 : Formulaire avec Relation et Table Secondaire**
```json
{
    "worflow1": {
        "tableMaster": {
            "table": "table_principal",
            "where": {
                "status": "workflow1",
                "type": 3
            },
            "color": "#356335",
            "update": {
                "status": "worflow1"
            }
        },
        "fields": {
            "code": {
                "label": "label1",
                "form": {
                    "type": "text",
                    "readonly": true,
                    "source_type": "session_var",
                    "source": "data.donnée_a_definir"
                },
                "security_key": "RegplITaXL4K"
            },
            "prd_or_cmp": {
                "label": "Produit u composant",
                "form": {
                    "type": "select",
                    "source": [
                        "item_enum1",
                        "item_enum2"
                    ],
                    "source_type": "enum"
                },
                "security_key": "SQ-FLUTkWN8c"
            }
        },
        "tableSecondaire": {
            "table": "table_secondaire",
            "label": "table secondaire",
            "relation": "principal_id_id",
            "expander": true,
            "count_records": true,
            "fields": {
                "incident_id": {
                    "label": "Id principal",
                    "form": {
                        "type": "text",
                        "readonly": true,
                        "source_type": "session_var",
                        "source": "data.principal_id"
                    },
                    "security_key": "J-xe4svrimhe"
                },
                "data1": {
                    "label": "Data 1",
                    "form": {
                        "type": "text"
                    },
                    "security_key": "t5L8DMCS8kN7"
                }
            }
        },
         "next_step": {
            "step": {
                "value": 3,
                "session-var": "data.step"
            },
            "entity_id": {
                "source": "id",
                "session-var": "data.incident_id"
            },
            "type_theme_ou_autre_data_de_classification": {
                "value": "cla",
                "session-var": "data.type"
            },
            "_id": {
                "value": 3,
                "session-var": "data._id"
            },
            "color": {
                "value": "#356335",
                "session-var": "data.color"
            },
            "next-page": "{nom_de_la_page_suivante}",
            "step_final": false
        },
        "form-buttons": {
            "security-key": "poing832nd",
            "label": "OK - Enregistré",
            "form-submit": {
                "type": "submit"
            }
        }
    },
    "worflow2":{}           
}
```
