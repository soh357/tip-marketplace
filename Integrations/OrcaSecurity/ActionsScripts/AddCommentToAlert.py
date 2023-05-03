from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from TIPCommon import extract_configuration_param, extract_action_param
from OrcaSecurityManager import OrcaSecurityManager
from constants import INTEGRATION_NAME, INTEGRATION_DISPLAY_NAME, ADD_COMMENT_TO_ALERT_SCRIPT_NAME


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ADD_COMMENT_TO_ALERT_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root",
                                           is_mandatory=True, print_value=True)
    api_key = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Key",
                                          is_mandatory=False)
    api_token = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Token",
                                            is_mandatory=False)
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             input_type=bool, print_value=True)

    # action parameters
    alert_id = extract_action_param(siemplify, param_name="Alert ID", is_mandatory=True, print_value=True)
    comment = extract_action_param(siemplify, param_name="Comment", is_mandatory=True, print_value=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    try:
        manager = OrcaSecurityManager(api_root=api_root, api_key=api_key, api_token=api_token, verify_ssl=verify_ssl,
                                      siemplify_logger=siemplify.LOGGER)

        alert_comment = manager.add_alert_comment(alert_id, comment)
        siemplify.result.add_result_json(alert_comment.to_json())
        result = True
        status = EXECUTION_STATE_COMPLETED
        output_message = f"Successfully added a comment to alert with ID \"{alert_id}\" in {INTEGRATION_DISPLAY_NAME}"

    except Exception as e:
        result = False
        status = EXECUTION_STATE_FAILED
        siemplify.LOGGER.error(f"General error performing action {ADD_COMMENT_TO_ALERT_SCRIPT_NAME}")
        siemplify.LOGGER.exception(e)
        output_message = f"Error executing action \"{ADD_COMMENT_TO_ALERT_SCRIPT_NAME}\". Reason: {e}"

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Status: {}".format(status))
    siemplify.LOGGER.info("Result: {}".format(result))
    siemplify.LOGGER.info("Output Message: {}".format(output_message))

    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
