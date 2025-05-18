
from peewee import *
from generate_app.z_apps._config.config import *

db = SqliteDatabase(
    DB_PATH,
    pragmas={
        'foreign_keys': 1,
        'journal_mode': 'WAL',
        'cache_size': -1024 * 64
    }
)

class BaseModel(Model):
    id = AutoField(primary_key=True)

    class Meta:
        database = db
        legacy_table_names = False

class RefAfterSales(BaseModel):
    satc = CharField(null=True)
    class Meta:
        table_name = 'ref_after_sales'

class RefBusiness(BaseModel):
    business = CharField(null=True)
    class Meta:
        table_name = 'ref_business'

class RefContexts(BaseModel):
    context = CharField(null=True)
    class Meta:
        table_name = 'ref_contexts'

class RefIncidentTypes(BaseModel):
    name = CharField(unique=False)
    description = TextField(null=True)
    color = CharField(null=True)
    prefix = CharField(null=True)
    class Meta:
        table_name = 'ref_incident_types'

class RefProductFamilies(BaseModel):
    name = CharField(unique=True)
    class Meta:
        table_name = 'ref_product_families'

class RefModels(BaseModel):
    name = CharField(unique=True)
    family = ForeignKeyField(RefProductFamilies, field='id', column_name='family_id', backref='models_by_family', null=True)
    #family = IntegerField(null=True)
    class Meta:
        table_name = 'ref_models'

class RefOccurences(BaseModel):
    code = CharField(null=True)
    description = TextField(null=True)
    class Meta:
        table_name = 'ref_occurences'

class RefSeverities(BaseModel):
    number = IntegerField(null=True)
    security = CharField(null=True)
    class Meta:
        table_name = 'ref_severities'

class RefPrioritiesM1(BaseModel):
    priority_m1 = CharField(null=True)
    severite = ForeignKeyField(RefSeverities, field='id', column_name='severite_id', backref='priorities_m1_by_severite', null=True)
    class Meta:
        table_name = 'ref_priorities_m1'

class RefPrioritiesM2(BaseModel):
    priority_m2 = CharField(null=True)
    occurence = ForeignKeyField(RefOccurences, field='id', column_name='occurence_id', backref='priorities_m2_by_occurence', null=True)
    class Meta:
        table_name = 'ref_priorities_m2'

class RefSites(BaseModel):
    name = CharField()
    code = CharField(unique=True)
    class Meta:
        table_name = 'ref_sites'

class RefState8D(BaseModel):
    code_state = CharField(null=True)
    title = CharField(null=True)
    description = TextField(null=True)
    class Meta:
        table_name = 'ref_state_8d'

class Users(BaseModel):
    name = CharField(null=True)
    email = CharField(null=True)
    profile = CharField(default='USER')
    idsso = CharField(null=True)
    is_active = IntegerField(default=1)
    class Meta:
        table_name = 'users'

class IncidentsAndQualifications(BaseModel):
    type = ForeignKeyField(RefIncidentTypes, field='id', column_name='type_id', backref='incident_by_type', null=True)
    ref = CharField(null=True)
    code = CharField(null=True)
    status = CharField(default='NEW')
    prd_or_cmp = CharField(null=True)
    product_family = ForeignKeyField(RefProductFamilies, field='id', column_name='product_family_id', backref='incident_by_product_family', null=True)
    model = ForeignKeyField(RefModels, field='id', column_name='model_id', backref='incident_by_model', null=True)
    serial_number = CharField(null=True)
    site = ForeignKeyField(RefSites,field='id', column_name='site_id', backref='incident_by_site', null=True)
    marches_pays = CharField(null=True)
    ref_designation = CharField(null=True)
    probleme_description = TextField(null=True)
    qte_fab = IntegerField(null=True)
    photos = TextField(null=True)
    complementary_information = TextField(null=True)
    sf_link = CharField(null=True)
    internal_or_wholesaler = CharField(null=True)
    project_number = CharField(null=True)
    wholesaler_name = CharField(null=True)
    context = ForeignKeyField(RefContexts, field='id', column_name='context_id', backref='incident_by_context', null=True)
    problems_in_relation = TextField(null=True)
    sap_link = CharField(null=True)
    priorisation_method = CharField(null=True)
    severity = ForeignKeyField(RefSeverities, field='id', column_name='severity_id', backref='incident_by_severity', null=True)
    occurence = ForeignKeyField(RefOccurences, field='id', column_name='occurence_id', backref='incident_by_occurence', null=True)
    priority_m1 = ForeignKeyField(RefPrioritiesM1, field='id', column_name='priority_m1_id', backref='incident_by_priority_m1', null=True)
    business = ForeignKeyField(RefBusiness, field='id', column_name='business_id', backref='incident_by_business', null=True)
    after_sales = ForeignKeyField(RefAfterSales, field='id', column_name='after_sales_id', backref='incident_by_after_sales', null=True)
    priority_m2 = ForeignKeyField(RefPrioritiesM2, field='id', column_name='priority_m2_id', backref='incident_by_priority_m2', null=True)
    ipr_value = DecimalField(max_digits=4, decimal_places=4, null=True)
    tag = CharField(null=True)
    emb_p1 = CharField(null=True)
    emb_p2 = CharField(null=True)
    emb_p3 = CharField(null=True)
    crise_p1 = IntegerField(default=0)
    crise_p2 = IntegerField(default=0)
    crise_p3 = IntegerField(default=0)
    d8 = CharField(null=True)
    qrqc_niv1 = CharField(null=True)
    corrective_action = TextField(null=True)
    no_action = CharField(null=True)
    lien_ector = CharField(null=True)
    state8 = ForeignKeyField(RefState8D, field='id', column_name='state8', backref='incident_by_state8', null=True)
    created_by = ForeignKeyField(Users, field='id', column_name='created_by', backref='incident_by_user', null=True)
    cr_date = DateField(null=True)
    upd_date = DateField(null=True),
    detection_date = DateField(null=True)
    class Meta:
        table_name = 'incidents_and_qualifications'

class NonConformities(BaseModel):
    wholesaler_name = CharField(null=True)
    sap_sk = CharField(null=True)
    non_conformity = TextField(null=True)
    iso_code = CharField(null=True)
    incident = ForeignKeyField(IncidentsAndQualifications, field='id', column_name='incident_id',  backref='non_conformities_by_incident', null=True)
    class Meta:
        table_name = 'non_conformities'

