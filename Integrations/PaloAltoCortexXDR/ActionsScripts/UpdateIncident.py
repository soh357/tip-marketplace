# Imports
from XDRManager import XDRManager
from SiemplifyAction import SiemplifyAction

# Consts.
PROVIDER_NAME = 'PaloAltoCortexXDR'


def main():
    # Configuration.
    siemplify = SiemplifyAction()

    siemplify.script_name = "Palo Alto Cortex XDR - Update Incident"
    siemplify.LOGGER.info("================= Main - Param Init =================")

    conf = siemplify.get_configuration(PROVIDER_NAME)
    api_root = conf.get('Api Root')
    api_key = conf.get('Api Key')
    api_key_id = conf.get('Api Key ID')
    verify_ssl = str(conf.get('Verify SSL', 'False')).lower() == 'true'

    xdr_manager = XDRManager(api_root, api_key, api_key_id, verify_ssl)

    # Parameters.
    incident_id = siemplify.parameters.get('Incident ID')
    assigned_user = siemplify.parameters.get('Assigned User Name')
    severity = siemplify.parameters.get('Severity')
    status = siemplify.parameters.get('Status')

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        xdr_manager.update_an_incident(incident_id, assigned_user=assigned_user, severity=severity, status=status)
        output_message = "Successfully update one or more fields of incident with ID: {0}".format(incident_id)
        result_value = "true"
    except Exception as e:
        siemplify.LOGGER.error("Failed to update incident: {}".format(incident_id))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("\n  result_value: {}\n  output_message: {}".format(result_value, output_message))
    siemplify.end(output_message, result_value)


if __name__ == '__main__':
    main()
