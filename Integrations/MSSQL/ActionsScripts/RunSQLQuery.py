from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from TIPCommon import extract_configuration_param, extract_action_param, construct_csv
from MSSQLManager import MSSQLManager
import json
import datetime


INTEGRATION_NAME = u"MSSQL"
SCRIPT_NAME = u"Run SQL Query"
RESULT_TABLE_HEADER = u"MSSQL Query Results"


def json_serial(obj):
    """
     JSON serializer for objects not serializable by default json code
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = u"{} - {}".format(INTEGRATION_NAME, SCRIPT_NAME)
    siemplify.LOGGER.info(u"----------------- Main - Param Init -----------------")

    server_addr = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Server Address")
    username = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Username")
    password = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Password")
    port = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Port",
                                       input_type=int)
    win_auth = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                           param_name=u"Windows Authentication", default_value=False, input_type=bool)
    use_kerberos = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                               param_name=u"Use Kerberos Authentication", default_value=False,
                                               input_type=bool)
    kerberos_realm = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Kerberos Realm")
    kerberos_username = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Kerberos Username")
    kerberos_password = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Kerberos Password")

    database = extract_action_param(siemplify, param_name=u"Database Name", is_mandatory=True)
    query = extract_action_param(siemplify, param_name=u"Query", is_mandatory=True)

    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name='Verify SSL',
                                             print_value=True, input_type=bool, is_mandatory=False,
                                             default_value=True)

    siemplify.LOGGER.info(u"----------------- Main - Started -----------------")

    try:
        sql_manager = MSSQLManager(username=username,
                                   password=password,
                                   server=server_addr,
                                   database=database,
                                   port=port,
                                   trusted=win_auth,
                                   use_kerberos=use_kerberos,
                                   kerberos_realm=kerberos_realm,
                                   kerberos_username=kerberos_username,
                                   kerberos_password=kerberos_password,
                                   verify_ssl=verify_ssl)

        siemplify.LOGGER.info(u"Connecting to SQL Server instance {}:{}.".format(server_addr, port))
        sql_manager.connect()

        # If no exception occur - then connection is successful
        siemplify.LOGGER.info(u"Connected successfully.")

        # Run search query
        results = sql_manager.executeQuery(query) or {}
        siemplify.LOGGER.info(u"Found {} results.".format(len(results)))

        if results:
            # Add results as CSV
            siemplify.LOGGER.info(u"Attaching results as CSV table.")
            siemplify.result.add_data_table(RESULT_TABLE_HEADER, construct_csv(results))
            output_message = u"Successfully finished search."

        else:
            # Query completed but no results were found
            output_message = u"No results were found."

        siemplify.result.add_result_json(json.dumps(results, default=json_serial))
        result_value = json.dumps(results, default=json_serial)
        status = EXECUTION_STATE_COMPLETED

    except Exception as e:
        siemplify.LOGGER.error(u"General error performing action {}. Error: {}".format(SCRIPT_NAME, e))
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = json.dumps({})
        output_message = u"General error performing action {}. Error: {}".format(SCRIPT_NAME, e)

    siemplify.LOGGER.info(u"----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(u"Status: {}:".format(status))
    siemplify.LOGGER.info(u"Result Value: {}".format(result_value))
    siemplify.LOGGER.info(u"Output Message: {}".format(output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()

