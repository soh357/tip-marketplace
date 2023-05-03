INTEGRATION_NAME = "Arcsight"


# ACTIONS
PING_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Ping")
SEARCH_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "SEARCH")
LIST_RESOURCES_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "List Resources")
ADD_ENTRIES_TO_ACTIVE_LIST_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Add Entries To Activelist")
GET_ACTIVE_LIST_ENTRIES_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Get Activelist Entries")
ADD_ENTITIES_TO_ACTIVE_LIST = "{} - {}".format(INTEGRATION_NAME, "Add Entities To Active List")
GET_QUERY_RESULTS_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Get Query Results")
IS_VALUE_IN_ACTIVELIST_COLUMN_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Is Value In Activelist Column")
GET_REPORT_ACTION_NAME = "{} - {}".format(INTEGRATION_NAME, "Get Report")
CHANGE_CASE_STAGE_SCRIPT_NAME = "{} - {}".format(INTEGRATION_NAME, "Change Case Stage")

# LIMIT DEFAULTS
DEFAULT_LIMIT = 100

CSV = "csv"

# VALID STAGES CONSTANT
VALID_STAGES = ['INITIAL', 'QUEUED', 'CLOSED', 'FINAL', 'FOLLOW_UP']


EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
DOMAIN_REGEX = r"[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})+"


# ADDITIONAL ENTITY TYPES
EMAIL_TYPE = 101
DOMAIN_TYPE = 102

UNSUPPORTED_REPORT_UUID_PREFIXES = ['94jAWS+']
