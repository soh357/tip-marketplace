INTEGRATION_IDENTIFIER = "Devo"
INTEGRATION_DISPLAY_NAME = "Devo"

# Actions:
PING_SCRIPT_NAME = "Ping"
ADVANCED_QUERY_SCRIPT_NAME = "Advanced Query"
SIMPLE_QUERY_SCRIPT_NAME = "Simple Query"

# Connectors:
ALERTS_CONNECTOR_NAME = "Devo Alerts Connector"

# Default values
TEST_CONNECTIVITY_STRING = "from siem.logtrust.alert.info"
CONNECTOR_TABLE_NAME = "siem.logtrust.alert.info"
TIME_FRAME_DEFAULT_VALUE = "Last Hour"
MAX_ROWS_TO_RETURN_DEFAULT_VALUE = 50
MAX_ROWS_TO_RETURN_MINIMUM_VALUE = 1
DEFAULT_OFFSET_TIME_IN_HOURS = 24
DEFAULT_MAX_ALERTS_PER_CYCLE = 30
DEFAULT_MINIMUM_PRIORITY_TO_FETCH = "Normal"

# Error Codes:
API_ERROR = 400
UNAUTHORIZED_ERROR = 401
BAD_QUERY_ERROR = 500

# Response Types:
JSON_MODE = 'json'

# Time frames:
TIME_FRAME_MAPPING = {
    "Last Hour": '1h',
    "Last 6 Hours": '6h',
    "Last 12 Hours": '12h',
    "Last 24 Hours": '24h',
    "Last Week": '7d',
    "Last Month": '30d'
}
CUSTOM_TIME_FRAME = "Custom"
NOW = 'now'
MINUTE = 60

# API Params Names:
QUERY = 'query'
FROM = 'from'
TO = 'to'
MODE = 'mode'
LIMIT = 'limit'
MODE_TYPE = 'type'

VERY_LOW_PRIORITY = "Very low"
LOW_PRIORITY = "Low"
NORMAL_PRIORITY = "Normal"
HIGH_PRIORITY = "High"
VERY_HIGH_PRIORITY = "Very high"
ALERT_PRIORITIES = [VERY_LOW_PRIORITY, LOW_PRIORITY, NORMAL_PRIORITY, HIGH_PRIORITY, VERY_HIGH_PRIORITY]

MAPPED_ALERT_PRIORITIES = {
    0.0: VERY_LOW_PRIORITY,
    3.0: LOW_PRIORITY,
    5.0: NORMAL_PRIORITY,
    7.0: HIGH_PRIORITY,
    10.0: VERY_HIGH_PRIORITY
}

REVERSED_MAPPED_ALERT_PRIORITIES = {
    VERY_LOW_PRIORITY: 0.0,
    LOW_PRIORITY: 3.0,
    NORMAL_PRIORITY: 5.0,
    HIGH_PRIORITY: 7.0,
    VERY_HIGH_PRIORITY: 10.0
}

ALERT_PRIORITY_TO_SIEM_SEVERITY = {
    0.0: -1,
    3.0: 40,
    5.0: 60,
    7.0: 80,
    10.0: 100
}

UNREAD_STATUS = "Unread"
UPDATED_STATUS = "Updated"
FALSE_POSITIVE_STATUS = "False positive"
WATCHED_STATUS = "Watched"
CLOSED_STATUS = "Closed"
REMINDER_STATUS = "Reminder"
RECOVERY_STATUS = "Recovery"
START_AF_STATUS = "Start_af"
ALERT_STATUSES = [UNREAD_STATUS, UPDATED_STATUS, FALSE_POSITIVE_STATUS, WATCHED_STATUS, CLOSED_STATUS, REMINDER_STATUS,
                  RECOVERY_STATUS, START_AF_STATUS]

MAPPED_ALERT_STATUSES = {
    0: UNREAD_STATUS,
    1: UPDATED_STATUS,
    2: FALSE_POSITIVE_STATUS,
    100: WATCHED_STATUS,
    300: CLOSED_STATUS,
    500: REMINDER_STATUS,
    600: RECOVERY_STATUS,
    700: START_AF_STATUS
}

REVERSED_MAPPED_ALERT_STATUSES = {
    UNREAD_STATUS: 0,
    UPDATED_STATUS: 1,
    FALSE_POSITIVE_STATUS: 2,
    WATCHED_STATUS: 100,
    CLOSED_STATUS: 300,
    REMINDER_STATUS: 500,
    RECOVERY_STATUS: 600,
    START_AF_STATUS: 700
}


# Other consts
WHITELIST_FILTER = 1
BLACKLIST_FILTER = 2
WHITELIST_FILTER_OPERATOR = "="
OR_OPERATOR = "or"
BLACKLIST_FILTER_OPERATOR = "/="  # Not equal
AND_OPERATOR = "and"  # Not equal
WHITELIST_BLACKLIST_PARAMETER_NAME = "context"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DEVO_ALERT_PREFIX = "Devo Alert"
DEVO_ALERT_DESCRIPTION = "Devo Alert Fetched"
UNIX_FORMAT = 1
STORED_IDS_LIMIT = 3000

