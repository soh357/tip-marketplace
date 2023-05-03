from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from TIPCommon import extract_configuration_param, extract_action_param
from IvantiEndpointManagerManager import IvantiEndpointManagerManager
from constants import INTEGRATION_NAME, INTEGRATION_DISPLAY_NAME, EXECUTE_QUERY_SCRIPT_NAME


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = EXECUTE_QUERY_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root",
                                           is_mandatory=True, print_value=True)
    username = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Username",
                                           is_mandatory=True, print_value=True)
    password = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Password",
                                           is_mandatory=True)
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             is_mandatory=True, input_type=bool, print_value=True)

    # Action parameters
    query = extract_action_param(siemplify, param_name="Query", is_mandatory=True, print_value=True)
    limit = extract_action_param(siemplify, param_name="Max Results To Return", input_type=int, print_value=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    result = True
    status = EXECUTION_STATE_COMPLETED
    output_message = ""
    json_results = {}

    try:
        if limit is not None and limit < 1:
            raise Exception("\"Max Results To Return\" must be greater than 0.")

        manager = IvantiEndpointManagerManager(api_root=api_root, username=username, password=password,
                                               verify_ssl=verify_ssl, siemplify_logger=siemplify.LOGGER)

        results = manager.execute_query(query, limit)

        if results:
            json_results["results"] = [result.to_json() for result in results]
            siemplify.result.add_result_json(json_results)
            output_message += f"Successfully execute query {query} in {INTEGRATION_DISPLAY_NAME}."
        else:
            output_message = f"No results were found for the query {query} in {INTEGRATION_DISPLAY_NAME}."

    except Exception as e:
        siemplify.LOGGER.error(f"General error performing action {EXECUTE_QUERY_SCRIPT_NAME}")
        siemplify.LOGGER.exception(e)
        result = False
        status = EXECUTION_STATE_FAILED
        output_message = f"Error executing action \"{EXECUTE_QUERY_SCRIPT_NAME}\". Reason: {e}"

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Status: {}".format(status))
    siemplify.LOGGER.info("Result: {}".format(result))
    siemplify.LOGGER.info("Output Message: {}".format(output_message))

    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
