-- Lisa tabelitele lühikesed kirjeldused ja täida lihtne andmevara register.
--
-- See samm ei muuda andmete sisu.
-- Ta muudab andmed paremini mõistetavaks järgmisele inimesele.

COMMENT ON TABLE intermediate.dim_products_scd IS
    'Toodete SCD Type 2 dimensioon. Iga rida kirjeldab ühte toote versiooni kehtivusvahemikuga.';
COMMENT ON COLUMN intermediate.dim_products_scd.valid_from IS
    'Kuupäev, millest alates see toote versioon kehtib.';
COMMENT ON COLUMN intermediate.dim_products_scd.valid_to IS
    'Viimane kuupäev, milleni see toote versioon kehtib.';

COMMENT ON TABLE intermediate.dim_stores_scd IS
    'Poodide SCD Type 2 dimensioon. Iga rida kirjeldab ühte poe versiooni kehtivusvahemikuga.';
COMMENT ON COLUMN intermediate.dim_stores_scd.valid_from IS
    'Kuupäev, millest alates see poe versioon kehtib.';
COMMENT ON COLUMN intermediate.dim_stores_scd.valid_to IS
    'Viimane kuupäev, milleni see poe versioon kehtib.';

COMMENT ON TABLE quality.order_rule_results IS
    'Andmekvaliteedi kontrollide tulemused. Üks rida tähistab üht ebaõnnestunud reeglit ühel toorreal.';
COMMENT ON COLUMN quality.order_rule_results.rule_name IS
    'Lühike masina- ja inimeseloetav reegli nimi.';

COMMENT ON TABLE quality.orders_clean IS
    'Tellimused, mis läbisid kõik kvaliteedikontrollid ja millele leiti sobiv dimensiooni versioon.';

COMMENT ON TABLE analytics.daily_product_sales_clean IS
    'Puhastatud päevane müügikoond. Siin on alles ainult read, mis läbisid kvaliteedikontrolli.';

COMMENT ON TABLE governance.data_asset_registry IS
    'Lihtne andmevara register. See aitab kirjeldada olulisemaid andmeobjekte ka ilma eraldi andmekataloogita.';

INSERT INTO governance.data_asset_registry (
    asset_name,
    asset_layer,
    asset_type,
    owner_name,
    steward_name,
    refresh_frequency,
    source_system,
    business_description,
    contains_personal_data,
    quality_notes,
    last_updated_at
)
VALUES
    (
        'staging.product_snapshots_raw',
        'staging',
        'table',
        'tootehaldur',
        'andmeinsener',
        'kord kuus',
        'kuised CSV snapshotid',
        'Toodete kuuseis. Kasutame seda toote versioonide ja hinnaootuste alusena.',
        FALSE,
        'Kontrolli, et product_id oleks snapshoti sees unikaalne ja et base_price_eur oleks täidetud.',
        NOW()
    ),
    (
        'staging.store_snapshots_raw',
        'staging',
        'table',
        'laologistika juht',
        'andmeinsener',
        'kord kuus',
        'kuised CSV snapshotid',
        'Poodide kuuseis. Kasutame seda poe nimetuse ja regiooni ajalooliseks sidumiseks.',
        FALSE,
        'Kontrolli, et store_id oleks snapshoti sees unikaalne.',
        NOW()
    ),
    (
        'staging.orders_raw',
        'staging',
        'table',
        'müügiprotsessi omanik',
        'andmeinsener',
        'iga praktikumi käivitus',
        'kohalik API',
        'Toorandmed kõigi tellimusridadega. Siin võivad olla ka vigased read.',
        FALSE,
        'Selles kihis ei filtreeri me vigu välja. Kvaliteedikontroll toimub hiljem.',
        NOW()
    ),
    (
        'quality.order_rule_results',
        'quality',
        'table',
        'andmehaldur',
        'andmeinsener',
        'iga kvaliteedijooks',
        'PostgreSQL kvaliteedikontrollid',
        'Koondtabel, kuhu kirjutame kõik ebaõnnestunud kvaliteedireeglid.',
        FALSE,
        'Iga staging_row_id võib siin esineda mitu korda, kui sama rida rikub mitut reeglit.',
        NOW()
    ),
    (
        'analytics.daily_product_sales_clean',
        'analytics',
        'table',
        'müügianalüütika omanik',
        'andmeinsener',
        'iga kvaliteedijooks',
        'quality.orders_clean',
        'Päevane müügikoond, mis sobib raporti või näidikulaua alusandmeks.',
        FALSE,
        'Siin on ainult read, mis läbisid kõik peamised kvaliteedikontrollid.',
        NOW()
    )
ON CONFLICT (asset_name) DO UPDATE SET
    asset_layer = EXCLUDED.asset_layer,
    asset_type = EXCLUDED.asset_type,
    owner_name = EXCLUDED.owner_name,
    steward_name = EXCLUDED.steward_name,
    refresh_frequency = EXCLUDED.refresh_frequency,
    source_system = EXCLUDED.source_system,
    business_description = EXCLUDED.business_description,
    contains_personal_data = EXCLUDED.contains_personal_data,
    quality_notes = EXCLUDED.quality_notes,
    last_updated_at = NOW();
