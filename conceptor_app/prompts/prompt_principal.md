# Contexte:
## Preambule
J'ai besoin d'une API (sous fastapi),  qui va comporter plusieurs routes, qui va permettre de fournir les différentes fonctionnalités de l'application concepteur pour son front-office. Cette application concepteur est basée sur le MDA (Model Driven Appliocation) ou MDS (Model Driven Software) et elle permet donc de générer à partir d'un cahier des charges PDF et d'un prompt : des modeles, des descripteurs et du code python en vue de construire une application. Elle a donc pour objectif de faire une application de type C.R.U.D avec un enchainement workflow (plus ou moins complexe) et de gérer quelques règles de gestion simples.
## Vérification / elligibilité 
La première fonctionnalité est de vérifier si le cahier des charges, ou les spécifications répondent aux critèrtes. En effet ce concepteur ne peut générer que des applications de gestion CRUD avec un enchainement de formulaire avbec plusieurs étapes répondant à un workflow avec quelques r!gles de gestion et de stableau de bord.
## Génération
A partir de ces modèles les gants IA vont générer : 
- un descripteur json (ex : saf_v2.json),
- le code SQL pour la base de données en adéquation avec le descripteur,
- le code python des pages spécifiques, le la BL, le base model, les interfaces, ect..
- l'instanciation de la class multi_step qui interprète le descripteur.
## Evolution
Une deuxième partie permet également de faire évoluer l'application existante. L'évolution de l'application se fait à partir des modèles mis à jour agrémenté d'un prompt.
## Espace documentaire
Pour la partie document, on trouve cinq catégories : 
- les documents fournies (Cahier des charges et autres annexes)
- les documents générés par les agents IA : diagramme d'archin, diagramme de séquences, ....
- les descripteurs
- le code et les scripts
- les templates d'aide à la génération
Cet espace permettra de stocker la mémoire du générateur pour gérer les itérations de la 1er génération et les évolutions. On retrouvera également les templates d'aide à la génération sur lesquels se basent les agents, qui eux aussi peuvent évoluer.
## Prompts des agents
Pour générer des applications basées sur le MDS, il y a besoin de plusieurs agents. Chaque agent aura un prompt initial, un CAG basé sur des templates d'aide ou de contrainte.
l'objectif est d'avoir un système un peu comme des GPTs qui permette de spécifier prompt, mémoire (CAG) et template.
## le CAG
L'objectif du CAG est de fournir une mémoire centralisée pour les agents. Il stockera :
- Les templates de structure nécessaires à la génération des documents et des fichiers,
- Les documents générés ou fournis pour les différentes phases,
- Les caches nécessaires pour permettre aux agents de gérer les itérations et les évolutions.

Le CAG permettra également de suivre l'évolution des templates et des documents, en assurant une traçabilité des modifications et des ajustements réalisés au cours des différentes phases de génération et d'évolution de l'application.

# Description des interfaces et des API nécessaires
Pour ce concepteur, on va retrouver plusieurs interfaces qui appelleront chacun de une à plusieurs routes de l'api.
## Les interfaces
on va donc retrouver les interfaces suivantes : 
### 1. Interface d'évaluation
Input initial: cahier des charges aux formats PDF (ou spécifications), et documents annexes si il y en a. Les formats acceptés sont : texte, markdown, pdf et éventuellement excel. Si il y a des images, elle passeront par un agents, qui fera la description au format markdown.
Output intermédiaire: Des questions complémentaires de l'agent IA, pour affiner son évaluation
Input secondaire : les réponses aux questions
Output final : score d'évaluation, historique des itérations, synthèse 
### 2. Interface de génération
- Input initial: cahier des charges aux formats PDF (ou spécifications), et documents annexes (même format que pour l'évaluation) et un prompt permettant d'apporter des compléments d'information.
pour chaque phase, les fichier fournies et généré après validation sont mis dans l'espacve documentaire.
#### **Itération 1 : diagramme de class et de séquence** 
- Output phase 1 : diagramme d'architecture, diagramme de séquence 
- Input phase 1 : demande de validation, si validé on passe à la phase 2, sinon on itère
#### **Itération 2 : Modèle de base de donnes**
- Output phase 2 : Modèle de base de données en SQL et code python de base_model (ORM peewee)
- Input phase 2 : demande de validation, si validé on passe à la phase 3, sinon on itère
#### **Itération 3 : Description de l'interface**
- Output phase 3 : Description des interfaces et des écran, avec les règles de gestion
- Input phase 3 : demande de validation, si validé on passe à la phase 4, sinon on itère
#### **Itération 4 : Structure des fichiers**
- Output phase 4 : Structure des fichiers au format markdown
- Input phase 4 : demande de validation, si validé on passe à la phase 5, sinon on itère
#### **Itération 5 : Génération des descripteurs json**
Il s'agit d'une des phases les plus importantes, les descipteurs doivent être en adéquation avec la base de donnnées, ils permettent de définir le comportement de l'application. Des class Python basé sur streamlit sont développées pour lire, interprété les descripteurs et générer le comportement de l'application.
Avant output, un agent spécifique doit vérifier ce que l'agent générateur des descripteurs à fait. Il doit mancer des script python de vérification du modèle, et un script python de génération des clés de sécurité. En parallèle un autre agent doit générer le fichier le dossier technique au format md
- Output phase 5 : Descripteurs JSON, les retour des check de validation et le dossier technique au format markdown
- Input phase 5 : demande de validation de chacuns des éléments, si tous validé, on passe à la phase 6, sinon on itère
#### **Itération 6 : Structure de l'application**
C'est une des phases qui peut demander des itérations intermédiaires, avec un traitement particulier pour chaque tâche.
Il s'agit d'un échange de type chatbot.
Output phase 6 : Demande à l'utilisateur en plus des interfaces et des pages streamlit pour les écran du descripteur, s'il souhaite traiter les éléments spécifgique repérer dans les documents initials. Une liste est renvoyée et l'agent IA demande les éléments spécifiques à traiter, comme par exemple : pages spécifiques, Authentifications éventuelle, Dashboard, Export
- Input phase 6 : Itères sur tous les éléments, réponds aux demandes de validation, Si validation
- Output définitif phase 6 : les élements validés
#### **Itération 7 : script d'installation**
- Output phase 7.1 : Demande quel moteur de base de données
- Input phase 7.1 : renseigne le moteur
- Agent IA => génération du fichier d'install et du requirements.txt
- Output phase 7.2 : demande validation
- Input 7.2 : validation ou itération
#### **Génération V0 de l'application** :
Création d'un ZIP versionné, si un repo GIT est renseigné, alors commit et push de la V0
- Output : Apoplication v0 générée, test effectué
#### **Itération d'ajustement**
Echange avec un agent spécifique pour éventuellement ajuster des éléments de l'application, des demande de développement spécifique additionnel peuvent être fait sur cette étape définitive
- Input et Output avec l'agent
- Output : les fichiers modifié
## Les agents                                      
1. Agent d'évaluation
**Rôle :** Évaluer le cahier des charges ou les spécifications pour vérifier leur éligibilité.
**Fonctionnalités :**
- Poser des questions complémentaires pour affiner l'évaluation.
- Générer un score d'évaluation, un historique des itérations, et une synthèse.
2. Agent de génération des diagrammes
**Rôle :** Générer les diagrammes d'architecture et de séquence.
**Fonctionnalités :**
- Produire des diagrammes pour la phase 1.
- Demander validation ou itérer.
3. Agent de génération des modèles de base de données
**Rôle :** Générer le modèle de base de données en SQL et le code Python du base_model.
**Fonctionnalités :**
- Produire les éléments pour la phase 2.
- Demander validation ou itérer.
4. Agent de description des interfaces
**Rôle :** Décrire les interfaces et les écrans, ainsi que les règles de gestion.
**Fonctionnalités :**
- Produire les descriptions pour la phase 3.
- Demander validation ou itérer.
5. Agent de structuration des fichiers
**Rôle :** Générer la structure des fichiers au format Markdown.
**Fonctionnalités :**
- Produire les structures pour la phase 4.
- Demander validation ou itérer.
6. Agent de génération des descripteurs JSON
**Rôle :** Générer les descripteurs JSON en adéquation avec la base de données.
**Fonctionnalités :**
- Vérifier les descripteurs générés.
- Lancer des scripts Python pour vérifier le modèle et générer des clés de sécurité.
- Générer un dossier technique au format Markdown.
- Demander validation ou itérer.
7. Agent de structuration de l'application
**Rôle :** Gérer les échanges de type chatbot pour structurer l'application.
**Fonctionnalités :**
- Demander des informations spécifiques à l'utilisateur (pages spécifiques, authentifications, dashboards, etc.).
- Produire les éléments validés pour la phase 6.
- Demander validation ou itérer.
8. Agent de génération des scripts d'installation
**Rôle :** Générer les fichiers d'installation et le requirements.txt.
**Fonctionnalités :**
- Demander le moteur de base de données.
- Produire les scripts pour la phase 7.
- Demander validation ou itérer.
9. Agent de génération de l'application V0
**Rôle :** Générer une version initiale de l'application.
**Fonctionnalités :**
- réer un ZIP versionné.
- Commit et push sur un dépôt Git si renseigné.
- Effectuer des tests.
10. Agent d'ajustement final
**Rôle :** Gérer les ajustements finaux et les demandes de développement additionnel.
**Fonctionnalités :**
- Échanger avec l'utilisateur pour ajuster les éléments de l'application.
- Répondre aux demandes spécifiques.
11. Agent de gestion documentaire (CAG)
**Rôle :** Gérer la mémoire des agents et les caches nécessaires.
**Fonctionnalités :**
- Stocker les documents générés et les templates d'aide.
- Permettre l'évolution des templates et des agents.
## Mise en place du CAG

# Architecture attendue
## Template de la file strucrture 
Voici le template de file structure qui doit être respecté 
 generate_app/
├── __init__.py
├── api.py **: Générer si besoin**
├── install_app.sh **: Générer**
├── webapp.py **: Générer**
├── _config/
│   └── config.py **: Générer**
├── _db/
│   ├── create_tables.sql **: Générer**
│   └── database.sqlite **: Exemple avec SQLite**
├── {page1}/ **: Générer**
│   └──{page1.1}.py **: Générer**
├── Admin/
│   ├── forms.py **: Fournies de base**
│   ├── references.py **: Générer si besoin**
│   └── {autre_fonction_admin}.py **: Générer si besoin**
├── {workflow}/ **: Générer si besoin**
│   ├── s1_.py **: Générer si besoin**
│   ├── s2_.py **: Générer si besoin**
│   └── sn_.py **: Générer si besoin**
├── z_apps/
│   ├── _config/
│   │   ├── config_pages.py **: Générer**
│   │   ├── db_connector3.py **: Générer**
│   │   └── config.py **: Générer**
│   ├── common/
│   │   ├── common_bl.py **: Fournies de base**
│   │   └── validate.py **: Fournies de base**
│   ├── interfaces/
│   │   ├──{home_or_dashboard}.py
│   │   ├── s1_{step}.py **: Générer si besoin**
│   │   ├── s2_{step}.py **: Générer si besoin**
│   │   ├── sn_{step}.py **: Générer si besoin**
│   │   └── json_wizard.py **: Fournies de base**
│   ├── middle_model/
│   │   ├── {descripteur1}.json **: Générer si besoin**
│   │   ├── {descripteur1}.json **: Générer si besoin**
│   │   ├── {descripteur1}.json **: Générer si besoin**
│   │   ├── description.md **: Fournies de base : documentation descripteur**
│   │   ├── dossier_technique.md **: Générer**
│   │   └── model_structure.md
│   ├── multi_steps/ **Class qui interprète les descripteurs, ne pas modifier**
│   │   ├── base/
│   │   │   ├── ms_helper.py **: Fournies de base**
│   │   │   ├── ms_base.py **: Fournies de base**
│   │   │   └── ms_json_utils.py **: Fournies de base**
│   │   └── view/
│   │       ├── ms_table_view.py **: Fournies de base**
│   │       ├── ms_form_view.py **: Fournies de base**
│   │       └── ms_inline_table_view.py **: Fournies de base**
│   ├── specific/
│   │   ├── base_model.py.py **: Générer**
│   │   ├── bl_{workflow}.py **: Générer**
│   │   ├── error_managment.py.py **: Fournie de base, mais à modfier si besoin**
│   │   └── {autre_fonction_specific}.py **: Générer si besoin**
└── README.md **: Générer**

## 📂 Inventaire « Fourni » vs « À générer »

| Catégorie | Fichiers **Fournis** (non modifiables) | Fichiers **À générer** |
|-----------|----------------------------------------|------------------------|
| **Core multi-step** | `ms_*/*.py`, `validate.py`, `json_wizard.py` | — |
| **Scripts d’aide** | `add_security_keys.py`, `description.md`, `model_structure.md` | — |
| **Templates & prompts** | stockés dans le CAG | — |
| **Descripteurs JSON** | — | `<entity>_vX.json` |
| **ORM & SQL** | `base_model.py` (générique) | `specific/base_model.py`, `create_tables.sql` |
| **Interfaces Streamlit** | — | `interfaces/*.py`, `webapp.py` |
| **BL spécifiques** | — | `specific/bl_<workflow>.py` |
| **Install & config** | — | `install_app.sh`, `_config/config.py`, `requirements.txt` |
| **Docs techniques** | — | `dossier_technique.md`, `README.md` |
| **Tests** | — | `tests/test_descriptors.py` (validation JSON-Schema) |

## 🔄 Interactions obligatoires envers l’utilisateur

1. **Choix du SGBD**  
   > _« Quel moteur de base de données souhaitez-vous ? (sqlite / MariaDB / PostgreSQL) »_

2. **Mode d’installation**  
   > _« Préférez-vous un déploiement **Docker**, un environnement **Poetry**, ou un simple **venv** ? »_

Les réponses sont stockées dans le CAG puis injectées :  
* SGBD → phase 2 (DDL + Peewee).  
* Mode d’installation → phase 7 (génération de `install_app.sh`, `requirements.txt`, éventuellement `Dockerfile` ou `pyproject.toml`).

### Authentification Azure AD (MS Entra)  
- Lors de la **phase 6**, l’agent Structuration demande :  
  « Souhaitez-vous activer l’authentification Microsoft Entra ? (oui/non) »  
- Si **oui** :  
  1. Génération de `auth.py` dans `Admin/` avec :  
     - décorateur `@requires_admin`,  
     - vérification JWT *Microsoft Identity Platform*,  
     - redirection login.  
  2. Ajout de `allowed_roles` **au niveau de chaque page Streamlit** du descripteur ;  
     valeurs par défaut : `["USER", "ADMIN"]`.  
  3. Variable d’env `AZURE_AD_TENANT_ID` à placer dans `_config/config.py`.

## 🧪 Politique de tests minimale

* **Phase 5** crée `tests/test_descriptors.py` qui vérifie :  
  `jsonschema.validate(descriptor, schema_v1) == OK`
* La CI exécute `pytest` ; réussite obligatoire pour passer à la phase 6.  
* Couverture globale ≥ 50 % au début ; pourra monter ensuite.

## ⚙️ Mapping fixe Agent ↔ Modèle LLM

| N° | Agent | Tâche principale | Modèle (Azure / Ollama) |
|----|-------|------------------|-------------------------|
| 1 | Évaluation | Comprendre le CDC | **gpt-4o** |
| 2 | Diagrammes | Archi & séquence | gpt-4o |
| 3 | DB / ORM | Raisonnement SQL | **o3-mini** |
| 4 | Interfaces | Description UI | **gemini-pro** |
| 5 | Structure fichiers | Markdown | llama-3 70B |
| 6 | Descripteurs JSON | Génération + vérifs | **codestral-22B** |
| 7 | Structuration app | Chatbot / tri | llama-3 70B |
| 8 | Install scripts | Shell / config | mistral-medium |
| 9 | ZIP & tests | Packaging | codestral-22B |
| 10 | Ajustements | Dév. add. | llama-3 70B |
| 11 | CAG | Mémoire & logs | llama-3 8B |
| **S** | **Supervisor** | Orchestration, cost-tracking | **o3-small** |

## 🧠 Rôle du Supervisor

* Valide chaque sortie : cohérence, coût, respect du schéma.  
* En cas d’échec, ré-oriente vers le même agent (max 2 itérations) puis escalade à l’humain.  
* Garde le total tokens & le coût Azure / local dans un fichier `cag/cost_report.json`.

## 📝 Règles CAG mises à jour

* **Contenu stocké** : prompts, réponses, templates, descripteurs, logs, reports.  
* **Non stocké** : code source Python/SQL/Dockerfile (géré par Git).  
* Traçabilité : chaque entrée possède `id`, `timestamp`, `agent`, `hash`.

## 🤖 Collaboration inter-agents (AutoGen)

Pour les tâches nécessitant davantage de raisonnement croisé, les agents peuvent
s’auto-questionner dans un **“groupe de réflexion”** orchestré par AutoGen.

### Exemple : génération conjointe des diagrammes (phase 1)

| Rôle AutoGen            | Spécialité                        | Modèle LLM |
|-------------------------|-----------------------------------|------------|
| **TechLeadAgent**       | Chef de projet technique ; vérifie la couverture fonctionnelle. | gpt-4o |
| **SeqDiagramAgent**     | Construit le diagramme de séquence. | gpt-4o |
| **ArchDiagramAgent**    | Construit le diagramme d’architecture. | gpt-4o |

1. **TechLeadAgent** lit le CDC, liste les cas d’usage.  
2. **SeqDiagramAgent** propose un premier diagramme ;  
   **ArchDiagramAgent** propose l’architecture.  
3. Boucle de 1 à 3 tours maximaux :  
   - chaque agent critique la proposition des autres,  
   - TechLead conclut sur la version finale synchronisée.  
4. Output unique consigné dans le CAG, validé par le Supervisor.

> Règle générale : tout groupe AutoGen doit se terminer soit par un **consensus**,
soit par une **escalade** au Supervisor après 3 tours infructueux.

## 📜 Conventions supplémentaires

| Élément        | Format                         | Exemple                               |
|----------------|--------------------------------|---------------------------------------|
| Tag Git        | v<MAJOR>.<MINOR>.<PATCH>       | v0.1.0                                |
| ZIP de build   | build_<timestamp>.zip          | build_2025-05-18_14-23-00.zip         |
| Fichier SQL    | _db/create_tables.sql          | (généré à la phase 2)                 |
| Script install | scripts/install_app.sh         | (ou Dockerfile / pyproject.toml)      |

## 🚀 Checklist de sortie pour V0

1. Descripteurs validés ✅  
2. Base Peewee & DDL générés ✅  
3. Streamlit pages + BL spécifiques placés ✅  
4. `install_app.sh` & `requirements.txt` générés ✅  
5. Tests JSON-Schema passés ✅  
6. ZIP créé **et** push Git (si repo configuré) ✅


# File structure du concepteur

conceptor_app/
├── README.md
├── requirements.txt
├── dockerfile
├── docker-compose.yml
├── install.sh
├── backend/
│   ├── api.py
│   ├── cag/
│   └── classes/
│       ├── model_validator_service.py
|       └── {autres_class}.py
├── espaces_documents/
├── frontend/
|   ├── home.py
|   ├── mes_apps/
|   ├── admin/
│   └── webapp.py
└── Agents/
    ├── working_agent_1_2_3.py
    └── agent1.py

