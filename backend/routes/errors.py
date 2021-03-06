"""
Routes to manages errors
"""
import os

from utils_flask_sqla.response import json_resp, csv_resp
from geonature.core.gn_permissions import decorators as permissions
from geonature.utils.env import DB

from ..api_error import GeonatureImportApiError
from ..blueprint import blueprint
from ..db.queries.user_errors import get_user_error_list
from ..db.queries.user_table_queries import (
    get_table_names,
    get_n_invalid_rows,
    get_invalid_data,
    get_delimiter,
    get_table_info,
)
from ..logs import logger
from ..utils.utils import get_upload_dir_path, get_pk_name


@blueprint.route("/get_error_list/<import_id>", methods=["GET"])
@permissions.check_cruved_scope("C", True, module_code="IMPORT")
@json_resp
def get_errors(info_role, import_id):
    errors = get_user_error_list(import_id)
    return {"errors": errors}


@blueprint.route("/check_invalid/<import_id>", methods=["GET", "POST"])
@permissions.check_cruved_scope("C", True, module_code="IMPORT")
@json_resp
def check_invalid(info_role, import_id):
    try:
        ARCHIVES_SCHEMA_NAME = blueprint.config["ARCHIVES_SCHEMA_NAME"]
        IMPORTS_SCHEMA_NAME = blueprint.config["IMPORTS_SCHEMA_NAME"]
        table_names = get_table_names(
            ARCHIVES_SCHEMA_NAME, IMPORTS_SCHEMA_NAME, int(import_id)
        )
        full_imports_table_name = table_names["imports_full_table_name"]
        n_invalid = get_n_invalid_rows(full_imports_table_name)
        return str(n_invalid), 200
    except Exception as e:
        logger.exception(e)
        raise GeonatureImportApiError(
            message="INTERNAL SERVER ERROR when getting invalid rows count",
            details=str(e),
        )


@blueprint.route("/get_errors/<import_id>", methods=["GET", "POST"])
@permissions.check_cruved_scope("C", True, module_code="IMPORT")
@csv_resp
def get_csv(info_role, import_id):
    """
    Export invalid data in CSV
    """
    try:
        # Set variables
        ARCHIVES_SCHEMA_NAME = blueprint.config["ARCHIVES_SCHEMA_NAME"]
        IMPORTS_SCHEMA_NAME = blueprint.config["IMPORTS_SCHEMA_NAME"]
        DIRECTORY_NAME = blueprint.config["UPLOAD_DIRECTORY"]
        MODULE_URL = blueprint.config["MODULE_URL"]
        PREFIX = blueprint.config["PREFIX"]
        INVALID_CSV_NAME = blueprint.config["INVALID_CSV_NAME"]

        uploads_directory = get_upload_dir_path(MODULE_URL, DIRECTORY_NAME)
        table_names = get_table_names(
            ARCHIVES_SCHEMA_NAME, IMPORTS_SCHEMA_NAME, int(import_id)
        )
        full_archive_table_name = table_names["archives_full_table_name"]
        full_imports_table_name = table_names["imports_full_table_name"]
        pk_name = get_pk_name(PREFIX)
        file_name = "_".join([INVALID_CSV_NAME, table_names["archives_table_name"]])
        full_file_name = ".".join([file_name, "csv"])
        full_path = os.path.join(uploads_directory, full_file_name)

        delimiter = get_delimiter(IMPORTS_SCHEMA_NAME, import_id)
        SEPARATOR_MAPPING = {"colon": ";", "tab": "\t", "space": " ", "comma": ","}

        conn = DB.engine.raw_connection()
        cur = conn.cursor()
        invalid_data_proxy = get_invalid_data(
            cur, full_archive_table_name, full_imports_table_name, full_path, pk_name,
        )
        columns = []
        invalid_data = []
        i = 0
        for row in invalid_data_proxy:
            temp = {}
            for col, val in row.items():
                if i == 0:
                    columns.append(col)
                temp[col] = val
            invalid_data.append(temp)
            i = i + 1
        return (full_file_name, invalid_data, columns, SEPARATOR_MAPPING.get(delimiter))

    except Exception as e:
        logger.error("*** SERVER ERROR when saving csv file of invalid data")
        logger.exception(e)
        raise GeonatureImportApiError(
            message="INTERNAL SERVER ERROR when saving csv file of invalid data",
            details=str(e),
        )
