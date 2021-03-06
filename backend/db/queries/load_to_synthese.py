from geonature.utils.env import DB

import pdb


def get_data_type(column_name):
    try:
        key_type = DB.session.execute(
            """
            SELECT data_type 
            FROM information_schema.columns
            WHERE table_name = 'synthese'
            AND column_name = '{column_name}';
            """.format(
                column_name=column_name
            )
        ).fetchone()[0]
        return key_type
    except Exception:
        raise


def insert_into_synthese(
    schema_name, table_name, select_part, total_columns, import_obj
):
    try:
        id_source = DB.session.execute(
            f"""
            SELECT id_source
            FROM gn_synthese.t_sources
            WHERE name_source = 'Import(id={import_obj.id_import})';
            """
        ).fetchone()[0]
        # insert user values in synthese
        query = """
            BEGIN;
            ALTER TABLE gn_synthese.synthese DISABLE TRIGGER tri_meta_dates_change_synthese;
            ALTER TABLE gn_synthese.synthese DISABLE TRIGGER tri_insert_cor_area_synthese;
            ALTER TABLE gn_synthese.synthese DISABLE TRIGGER tri_update_cor_area_taxon_update_cd_nom;

            INSERT INTO gn_synthese.synthese ({into_part})
            SELECT {select_part}
            FROM {schema_name}.{table_name}
            WHERE gn_is_valid='True';

            ALTER TABLE gn_synthese.synthese ENABLE TRIGGER tri_meta_dates_change_synthese;
            ALTER TABLE gn_synthese.synthese ENABLE TRIGGER tri_insert_cor_area_synthese;
            ALTER TABLE gn_synthese.synthese ENABLE TRIGGER tri_update_cor_area_taxon_update_cd_nom;
            COMMIT;            
            
            """.format(
            into_part=",".join(total_columns.keys()),
            select_part=",".join(select_part),
            schema_name=schema_name,
            table_name=table_name,
        )
        DB.session.execute(query)

        # update last_action in synthese
        DB.session.execute(
            f"""
            -- restore trigger
            -- cor_area_synthese
            BEGIN;
            ALTER TABLE gn_synthese.cor_area_synthese DISABLE TRIGGER tri_maj_cor_area_taxon;

            INSERT INTO gn_synthese.cor_area_synthese
            SELECT
            s.id_synthese,
            a.id_area
            FROM ref_geo.l_areas a
            JOIN gn_synthese.synthese s ON public.st_intersects(s.the_geom_local, a.geom)
            WHERE a.enable = true AND s.id_source = {id_source}
            ;
            ALTER TABLE gn_synthese.cor_area_synthese ENABLE TRIGGER tri_maj_cor_area_taxon;

            COMMIT;

            BEGIN;
            -- cor area_taxon
            DELETE from gn_synthese.cor_area_taxon cat
            WHERE cat.cd_nom in (SELECT DISTINCT cd_nom from gn_synthese.synthese where id_source ={id_source});

            INSERT INTO gn_synthese.cor_area_taxon (cd_nom, nb_obs, id_area, last_date)
            SELECT s.cd_nom, count(s.id_synthese), cor.id_area,  max(s.date_min)
            FROM gn_synthese.cor_area_synthese cor
            JOIN gn_synthese.synthese s ON s.id_synthese = cor.id_synthese
            WHERE s.id_source = {id_source}
            GROUP BY cor.id_area, s.cd_nom;
            COMMIT;

            BEGIN;
            UPDATE gn_synthese.synthese SET meta_create_date = NOW() WHERE meta_create_date IS NULL;
            UPDATE gn_synthese.synthese SET meta_update_date = NOW() WHERE meta_update_date IS NULL;
            UPDATE gn_synthese.synthese
            SET last_action = 'I'
            WHERE id_source = {id_source};
            COMMIT;
        """
        )

        DB.session.flush()
    except Exception:
        DB.session.rollback()
        raise


def insert_into_t_sources(schema_name, table_name, import_id, total_columns):
    try:
        DB.session.execute(
            """
            INSERT INTO gn_synthese.t_sources(name_source,desc_source,entity_source_pk_field,url_source) VALUES
            (
                'Import(id={import_id})',
                'Imported data from import module (id={import_id})',
                '{schema_name}.{table_name}.{entity_col_name}',
                NULL
            )
            """.format(
                import_id=import_id,
                entity_col_name=total_columns.get("entity_source_pk_value", None),
                schema_name=schema_name,
                table_name=table_name,
            )
        )
        DB.session.flush()
    except Exception:
        DB.session.rollback()
        raise


def get_id_source(import_id):
    try:
        id_source = DB.session.execute(
            """
            SELECT id_source
            FROM gn_synthese.t_sources
            WHERE name_source = 'Import(id={import_id})'
            """.format(
                import_id=import_id
            )
        ).fetchone()[0]
        return id_source
    except Exception:
        raise


def check_id_source(import_id):
    try:
        is_id_source = DB.session.execute(
            """
            SELECT exists (
                SELECT 1 
                FROM gn_synthese.t_sources 
                WHERE name_source = 'Import(id={import_id})' 
                LIMIT 1);
            """.format(
                import_id=import_id
            )
        ).fetchone()[0]
        return is_id_source
    except Exception:
        raise


def get_synthese_info(selected_synthese_cols):
    formated_selected_synthese_cols = "','".join(selected_synthese_cols)
    formated_selected_synthese_cols = "{}{}{}".format(
        "('", formated_selected_synthese_cols, "')"
    )

    synthese_info = DB.session.execute(
        """
        SELECT column_name,is_nullable,column_default,data_type,character_maximum_length\
        FROM INFORMATION_SCHEMA.COLUMNS\
        WHERE table_name = 'synthese'\
        AND column_name IN {};""".format(
            formated_selected_synthese_cols
        )
    ).fetchall()

    my_dict = {
        d[0]: {
            "is_nullable": d[1],
            "column_default": d[2],
            "data_type": d[3],
            "character_max_length": d[4],
        }
        for d in synthese_info
    }

    return my_dict
