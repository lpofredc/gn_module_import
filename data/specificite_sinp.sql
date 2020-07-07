UPDATE gn_imports.dict_fields
SET display = FALSE 
WHERE name_field IN (
    'id_nomenclature_sensitivity',
    'id_digitiser',
    'meta_v_taxref',
    'meta_create_date',
    'meta_update_date'
);


-- Permissions groupe admin sur import
INSERT INTO gn_permissions.cor_role_action_filter_module_object
    (
    id_role,
    id_action,
    id_filter,
    id_module,
    id_object
    )
VALUES
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 1, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 2, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 3, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 6, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1)
;

-- groupe producteur import désactivé
INSERT INTO gn_permissions.cor_role_action_filter_module_object
    (
    id_role,
    id_action,
    id_filter,
    id_module,
    id_object
    )
VALUES
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 1, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 2, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 3, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 6, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), 1)
;


INSERT INTO gn_permissions.cor_role_action_filter_module_object
    (
    id_role,
    id_action,
    id_filter,
    id_module,
    id_object
    )
VALUES
    -- Groupe Admin sur objet mapping
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 1, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 2, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 3, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin' AND groupe IS TRUE), 6, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING'))
;

    INSERT INTO gn_permissions.cor_role_action_filter_module_object
    (
    id_role,
    id_action,
    id_filter,
    id_module,
    id_object
    )
VALUES
    -- Groupe producteur sur objet mapping
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 1, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 2, 4, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 3, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING')),
    ((SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Producteur' AND groupe IS TRUE), 6, 1, (SELECT id_module FROM gn_commons.t_modules WHERE module_code='IMPORT'), (SELECT id_object FROM gn_permissions.t_objects WHERE code_object = 'MAPPING'))
;