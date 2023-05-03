from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
from FireEyeHelixConstants import PROVIDER_NAME, ADD_NOTE_TO_ALERT_SCRIPT_NAME
from TIPCommon import extract_configuration_param, extract_action_param
from FireEyeHelixManager import FireEyeHelixManager
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from FireEyeHelixExceptions import FireEyeHelixNotFoundAlertException


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ADD_NOTE_TO_ALERT_SCRIPT_NAME
    result_value = True
    status = EXECUTION_STATE_COMPLETED

    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    # Init Integration Configurations
    api_root = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="API Root",
        is_mandatory=True
    )

    api_token = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="API Token",
        is_mandatory=True
    )

    verify_ssl = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="Verify SSL",
        is_mandatory=True,
        input_type=bool
    )

    # Init Action Parameters
    alert_id = extract_action_param(siemplify, param_name='Alert ID', is_mandatory=True)
    note = extract_action_param(siemplify, param_name='Note', is_mandatory=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    try:
        manager = FireEyeHelixManager(
            api_root=api_root,
            api_token=api_token,
            verify_ssl=verify_ssl,
            siemplify=siemplify
        )
        manager.add_note_to_alert(alert_id, note)
        output_message = "Successfully added a note to the alert with ID {id} in FireEye Helix."\
            .format(id=alert_id)

    except FireEyeHelixNotFoundAlertException:
        output_message = "Action wasn't able to add a note to the alert with ID {id} in FireEye Helix. " \
                         "Reason: Alert with ID {id} wasn't found.".format(id=alert_id)
        result_value = False
    except Exception as e:
        output_message = "Error executing action \"Add Note To Alert\". Reason: {}".format(e)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info('Status: {}'.format(status))
    siemplify.LOGGER.info('Result: {}'.format(result_value))
    siemplify.LOGGER.info('Output Message: {}'.format(output_message))

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
