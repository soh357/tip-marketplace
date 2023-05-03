from SiemplifyUtils import output_handler
from TIPCommon import extract_action_param, extract_configuration_param
from SiemplifyAction import SiemplifyAction
from QRadarManager import QRadarManager
from exceptions import QRadarValidationError
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from constants import (
    INTEGRATION_NAME,
    LIST_REFERENCE_SETS_SCRIPT_NAME,
    LIMIT
)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = LIST_REFERENCE_SETS_SCRIPT_NAME

    siemplify.LOGGER.info('----------------- Main - Param Init -----------------')

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name='API Root',
                                           is_mandatory=True)
    api_token = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name='API Token',
                                            is_mandatory=True)
    api_version = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name='API Version')

    siemplify.LOGGER.info('----------------- Main - Started -----------------')

    status = EXECUTION_STATE_COMPLETED
    result_value = True

    try:
        fields_to_return = extract_action_param(siemplify, param_name='Fields To Return', is_mandatory=False,
                                                print_value=True)
        filter_condition = extract_action_param(siemplify, param_name='Filter Condition', is_mandatory=False,
                                                print_value=True)
        results_limit = extract_action_param(siemplify, param_name='Number Of Elements To Return', is_mandatory=True,
                                             input_type=int, print_value=True)

        if results_limit < 0:
            results_limit = LIMIT
            siemplify.LOGGER.info(f"Number Of Elements To Return parameter is negative. Using default value of {LIMIT}")

        manager = QRadarManager(api_root, api_token, api_version)
        reference_sets = manager.get_reference_sets(fields_to_return, filter_condition, results_limit)
        if reference_sets:
            output_message = "Action completed successfully and returned data."
            siemplify.result.add_result_json([ref_set.to_json() for ref_set in reference_sets])
        else:
            output_message = "Action completed successfully but didn't return any data."

    except QRadarValidationError as e:
        output_message = f"Failed to execute action due to errors: {e}."
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        result_value = False

    except Exception as e:
        output_message = f'Error executing {LIST_REFERENCE_SETS_SCRIPT_NAME}. Reason {e}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.LOGGER.info('----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(f'\n  status: {status}\n  result_value: {result_value}\n  output_message: {output_message}')
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    main()
