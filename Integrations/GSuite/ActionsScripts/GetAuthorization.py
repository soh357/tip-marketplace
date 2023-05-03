from TIPCommon import extract_configuration_param, extract_action_param

from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from consts import (
    INTEGRATION_NAME,
    GET_AUTHORIZATION_SCRIPT_NAME,
    AUTHORIZATION_URL
)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "{} - {}".format(INTEGRATION_NAME, GET_AUTHORIZATION_SCRIPT_NAME)
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    # INTEGRATION Configuration
    client_id = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                            param_name="Client ID")

    # Action configuration
    redirect_url = extract_action_param(siemplify, param_name="Redirect URL", is_mandatory=True, print_value=True)
    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    try:
        auth_link = AUTHORIZATION_URL.format(client_id=client_id, redirect_uri=redirect_url)
        siemplify.result.add_link("Browse to this authorization link", auth_link)
        output_message = "Your browser should be redirected with a code in the address bar. In order to complete the registration, run 'Generate Token' action with the received url in the address bar."
        status = EXECUTION_STATE_COMPLETED
        result_value = True
    except Exception as error:
        output_message = f'Error executing action {GET_AUTHORIZATION_SCRIPT_NAME}. Reason: {error}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(error)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.LOGGER.info('----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(f"Status: {status}")
    siemplify.LOGGER.info(f"Result Value: {result_value}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    main()
