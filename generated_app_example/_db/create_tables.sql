CREATE TABLE "ref_after_sales"(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	satc TEXT
);

CREATE TABLE "ref_business"(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	business TEXT
);

CREATE TABLE "ref_contexts"(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	context TEXT
);

CREATE TABLE "ref_incident_types" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT, 
	color TEXT,
	prefix TEXT
);


CREATE TABLE "ref_product_families" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);


CREATE TABLE "ref_models" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    family_id INTEGER,
    FOREIGN KEY(family_id) REFERENCES ref_product_families(id)
);

CREATE TABLE "ref_occurences" (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	code TEXT,
	description TEXT
);

CREATE TABLE "ref_severities" (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	number INT,
	security TEXT
);

CREATE TABLE ref_priorities_m1 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	priority_m1 TEXT,
	severite_id INTEGER,
	FOREIGN KEY (severite_id) REFERENCES ref_severities(id)
);

CREATE TABLE ref_priorities_m2 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	priority_m2 TEXT,
	occurence_id INTEGER,
	FOREIGN KEY (occurence_id) REFERENCES ref_occurences(id)
);

CREATE TABLE "ref_sites" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL
);

CREATE TABLE "ref_state_8d"(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	code_state TEXT,
	title TEXT,
	Description TEXT
);

CREATE TABLE "users" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    profile TEXT DEFAULT 'USER',
    idsso TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE incidents_and_qualifications (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	type_id INTEGER,
	code TEXT,
	ref TEXT,
	status TEXT,
	prd_or_cmp TEXT,
	product_family_id INTEGER,
	model_id INTEGER,
	serial_number TEXT,
	site_id INTEGER,
	marches_pays TEXT,
	ref_designation TEXT,
	probleme_description TEXT,
	qte_fab INTEGER,
	photos TEXT,
	complementary_information TEXT,
	sf_link TEXT,
	internal_or_wholesaler TEXT,
	project_number TEXT,
	wholesaler_name TEXT,
	context_id INTEGER,
	detection_state TEXT
	factory TEXT,
	problems_in_relation TEXT,
	sap_link TEXT,
	priorisation_method TEXT,
	severity_id INTEGER,
	occurence_id INTEGER,
	priority_m1_id INTEGER,
	business_id INTEGER,
	after_sales_id INTEGER,
	priority_m2_id INTEGER,
	ipr_value DECIMAL,
	tag TEXT,
	emb_p1 TEXT,
	emb_p2 TEXT,
	emb_p3 TEXT,
	crise_p1 INTEGER,
	crise_p2 INTEGER,
	crise_p3 INTEGER,
	d8 TEXT,
	qrqc_niv1 TEXT,
	corrective_action TEXT,
	no_action TEXT,
	lien_ector TEXT,
	state8 INTEGER,
	created_by INTEGER,
	cr_date DATE,
	upd_date DATE,
	detection_date DATE,
	FOREIGN KEY (type_id) REFERENCES ref_incident_types(id),
	FOREIGN KEY (product_family_id) REFERENCES ref_product_families(id),
	FOREIGN KEY (model_id) REFERENCES ref_models(id),
	FOREIGN KEY (after_sales_id) REFERENCES ref_after_sales(id),
	FOREIGN KEY (business_id) REFERENCES ref_business(id),
	FOREIGN KEY (context_id) REFERENCES ref_contexts(id),
	FOREIGN KEY (priority_m1_id) REFERENCES ref_priorities_m1(id),
	FOREIGN KEY (occurence_id) REFERENCES ref_occurences(id),
	FOREIGN KEY (priority_m2_id) REFERENCES ref_priorities_m2(id),
	FOREIGN KEY (severity_id) REFERENCES ref_severities(id),
	FOREIGN KEY (site_id) REFERENCES ref_sites(id),
	FOREIGN KEY (created_by) REFERENCES users(id)
);


CREATE TABLE "non_conformities"(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	wholesaler_name TEXT,
	sap_sk TEXT,
	non_conformity TEXT,
	iso_code TEXT,
	incident_id INTEGER,
	FOREIGN KEY(incident_id) REFERENCES incidents_and_qualifications(id)
);

INSERT INTO users
(id, name, email, profile, idsso, is_active)
VALUES(1, 'Admin', 'admin@adin', 'ADMIN', 'SSO1', 1);
INSERT INTO users
(id, name, email, profile, idsso, is_active)
VALUES(2, 'User', 'user@User', 'USER', 'SSO2', 1);

INSERT INTO ref_state_8d
(id, code_state, title, Description)
VALUES(1, 'D1', 'Establish the team', 'Dans Sharepoint');
INSERT INTO ref_state_8d
(id, code_state, title, Description)
VALUES(2, 'D2', 'Describe the problem', 'Description dans Sharepoint');
INSERT INTO ref_state_8d
(id, code_state, title, Description)
VALUES(3, 'D3', 'Implement containment / short-term / Interim actions', NULL);
INSERT INTO ref_state_8d
(id, code_state, title, Description)
VALUES(4, 'D4', 'Identify and verify root causes', NULL);

INSERT INTO ref_sites
(id, name, code)
VALUES(1, 'Site Paris', 'PAR');
INSERT INTO ref_sites
(id, name, code)
VALUES(2, 'Site Lyon', 'LYO');
INSERT INTO ref_sites
(id, name, code)
VALUES(3, 'Site Marseille', 'MAR');

INSERT INTO ref_severities
(id, "number", "security")
VALUES(1, 10, 'Problème sécurit');
INSERT INTO ref_severities
(id, "number", "security")
VALUES(2, 7, 'Perte de fonction principale ou incident client majeur');
INSERT INTO ref_severities
(id, "number", "security")
VALUES(3, 5, 'Réduction significative de performance ou de confort');

INSERT INTO ref_product_families
(id, name)
VALUES(1, 'ECS');
INSERT INTO ref_product_families
(id, name)
VALUES(2, 'BOILER');
INSERT INTO ref_product_families
(id, name)
VALUES(3, 'PAC');
INSERT INTO ref_product_families
(id, name)
VALUES(4, 'Clim/Ventil');
INSERT INTO ref_product_families
(id, name)
VALUES(5, 'Composants');

INSERT INTO ref_models
(id, name, family_id)
VALUES(1, 'E-Model-001', 1);
INSERT INTO ref_models
(id, name, family_id)
VALUES(2, 'M-Model-001', 2);
INSERT INTO ref_models
(id, name, family_id)
VALUES(3, 'C-Model-001', 3);


INSERT INTO ref_occurences
(id, code, description)
VALUES(1, 'B3.1', 'BOILER 3em génération');
INSERT INTO ref_occurences
(id, code, description)
VALUES(2, 'P1.2', 'PAC v2');
INSERT INTO ref_occurences
(id, code, description)
VALUES(3, 'P2.1', 'CLIM NAVICLIM');

INSERT INTO ref_incident_types
(id, name, description, color, prefix)
VALUES(1, 'Custummer Incident', 'Incident client, avec alerte spécifique / récurrence / ayant fait l’objet d’un échange en point qualité/après-vente', 'red', NULL);
INSERT INTO ref_incident_types
(id, name, description, color, prefix)
VALUES(2, 'Project incident', 'Incident projet, détecté après la phase de faisabilité', 'orange', NULL);
INSERT INTO ref_incident_types
(id, name, description, color, prefix)
VALUES(3, 'Safety alert', 'Alerte Safety venant du terrain, (+ atelier fab, incidents liés au produit ?)', 'green', NULL);
INSERT INTO ref_incident_types
(id, name, description, color, prefix)
VALUES(4, 'International non-conformance', 'Non-conformité interne (production, R&D hors projet, logistique, achats)', 'blue', NULL);
INSERT INTO ref_incident_types
(id, name, description, color, prefix)
VALUES(5, 'Supplier non-conformance', 'Non conformlité fournisseur', 'purple', NULL);

INSERT INTO ref_contexts
(id, context)
VALUES(1, 'Field test ');
INSERT INTO ref_contexts
(id, context)
VALUES(2, 'Labo (valid)');
INSERT INTO ref_contexts
(id, context)
VALUES(3, 'Labo (certif) ');
INSERT INTO ref_contexts
(id, context)
VALUES(4, 'Essai par le fournisseur');

INSERT INTO ref_business
(id, business)
VALUES(1, 'Blocage');
INSERT INTO ref_business
(id, business)
VALUES(2, 'Mineur');

INSERT INTO ref_after_sales
(id, satc)
VALUES(1, 'CRT1');
INSERT INTO ref_after_sales
(id, satc)
VALUES(2, 'CRT2');
INSERT INTO ref_after_sales
(id, satc)
VALUES(3, 'CRT3');


