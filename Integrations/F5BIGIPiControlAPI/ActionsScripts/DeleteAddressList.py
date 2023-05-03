from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from TIPCommon import extract_configuration_param, extract_action_param
from F5BIGIPiControlAPIManager import F5BIGIPiControlAPIManager
from constants import INTEGRATION_NAME, INTEGRATION_DISPLAY_NAME, DELETE_ADDRESS_LIST_NAME
from F5BIGIPiControlAPIExceptions import InvalidInputException

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = DELETE_ADDRESS_LIST_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root",
                                           is_mandatory=True, print_value=True)
    username = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Username",
                                           is_mandatory=True, print_value=True)
    password = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Password",
                                           is_mandatory=True)
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             input_type=bool, is_mandatory=True, print_value=True)

    # Action parameters
    list_name = extract_action_param(siemplify, param_name="Name", is_mandatory=True, print_value=True)
    
    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    result = True
    status = EXECUTION_STATE_COMPLETED

    try:
        manager = F5BIGIPiControlAPIManager(api_root=api_root,
                                            username=username,
                                            password=password,
                                            verify_ssl=verify_ssl,
                                            siemplify_logger=siemplify.LOGGER)

        manager.delete_address_list(list_name=list_name)
        output_message = f"Successfully deleted address list {list_name} in {INTEGRATION_DISPLAY_NAME}."

    except InvalidInputException:
        output_message = f"Address list {list_name} doesn't exist in {INTEGRATION_DISPLAY_NAME}."

    except Exception as e:
        siemplify.LOGGER.error(f"General error performing action {DELETE_ADDRESS_LIST_NAME}")
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result = False
        output_message = f"Error executing action \"{DELETE_ADDRESS_LIST_NAME}\". Reason: {e}"

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Status: {}".format(status))
    siemplify.LOGGER.info("Result: {}".format(result))
    siemplify.LOGGER.info("Output Message: {}".format(output_message))

    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
