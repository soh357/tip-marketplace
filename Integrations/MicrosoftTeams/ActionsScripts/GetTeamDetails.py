from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import dict_to_flat, flat_dict_to_csv
from MicrosoftManager import MicrosoftTeamsManager
import json
from TIPCommon import extract_configuration_param,extract_action_param
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from MicrosoftConstants import (
    INTEGRATION_NAME,
    GET_TEAM_DETAILS_ACTION
)

@output_handler
def main():

    siemplify = SiemplifyAction()
    siemplify.script_name = GET_TEAM_DETAILS_ACTION
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    client_id = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                                  param_name="Client ID", is_mandatory=True, print_value=True)
    secret_id = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                                  param_name="Secret ID", is_mandatory=True, print_value=False)
    tenant = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                                  param_name="Tenant", is_mandatory=True, print_value=True)
    token = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                                  param_name="Refresh Token", is_mandatory=True, print_value=False)
    redirect_url = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME,
                                                  param_name="Redirect URL", is_mandatory=False, print_value=True)    

    team_name = extract_action_param(siemplify, param_name="Team Name", print_value=True, is_mandatory=True)
 
    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    status = EXECUTION_STATE_COMPLETED
    result_value = True
    output_message = ""
    
    try:
        mtm = MicrosoftTeamsManager(client_id, secret_id, tenant, token, redirect_url)
        team_details = mtm.get_team_details(team_name)
        json_results = {}

        if team_details:
            json_results = team_details
            flat_report = dict_to_flat(team_details)
            csv_output = flat_dict_to_csv(flat_report)
            siemplify.result.add_data_table("Team details - {}".format(team_name), csv_output)
            output_message = 'Found details for team {}'.format(team_name)
            result_value = json.dumps(team_details)
        else:
            output_message = 'No details found for team - {}.'.format(team_name)
            result_value = json.dumps({})

        siemplify.result.add_result_json(json_results)
        
    except Exception as e:
        output_message = f'Error executing action {GET_TEAM_DETAILS_ACTION}. Reason: {e}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.LOGGER.info('----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(
        f"\n  status: {status}\n  result_value: {result_value}\n  output_message: {output_message}")
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    main()