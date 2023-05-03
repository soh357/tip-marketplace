from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes
from SiemplifyAction import SiemplifyAction
from SEPManager import SEP14Manager, COMPLETED, STATUS
from TIPCommon import extract_configuration_param

INTEGRATION_NAME = "SEP"
ACTION_NAME = "SEP - Enable Download Insight"
COMMAND = "sep_enable_download_insight_command_id"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    output_message = ""
    errors = ""

    siemplify.LOGGER.info("Starting Action")

    conf = siemplify.get_configuration('SEP')
    username = conf["Username"]
    password = conf["Password"]
    domain = conf["Domain"]
    url = conf["Api Root"]
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name='Verify SSL',
                                             input_type=bool, default_value=False)
    sep_manager = SEP14Manager(url, username, password, domain, verify_ssl=verify_ssl)
    siemplify.LOGGER.info("Connected.")

    enriched_entities = []

    for entity in siemplify.target_entities:
        try:
            computer_id = None

            if entity.entity_type == EntityTypes.ADDRESS:
                computer_id = sep_manager.getComputerIdByIP(entity.identifier)

            elif entity.entity_type == EntityTypes.HOSTNAME:
                computer_info = sep_manager.getComputerInfo(entity.identifier)
                if computer_info:
                    computer_id = sep_manager.getComputerIdByComputerName(
                        computer_info["computerName"])

            if computer_id:
                siemplify.LOGGER.info("Enabling DownloadInsight on {}".format(entity.identifier))

                command_id = sep_manager.runClientCommandEnableDownloadInsight(
                    computer_id)

                entity.additional_properties.update({
                    COMMAND: command_id,
                })

                enriched_entities.append(entity)

        except Exception as e:
            errors += "Enabling Download Insight failed on {0}:\n{1}\n".format(entity.identifier, e.message)
            siemplify.LOGGER.error(
                "An error occurred on entity: {}.\n{}.".format(
                    entity.identifier, str(e)
                ))
            siemplify.LOGGER.exception(e)
            continue

    if enriched_entities:
        entities_names = ["{0}: {1}\n".format(entity.identifier,
                                              entity.additional_properties[COMMAND]) for entity in enriched_entities]

        output_message += 'Enabling Download Insight on the following entities:\n' + '\n'.join(
            entities_names)
        output_message += errors

        siemplify.update_entities(enriched_entities)
        siemplify.end(output_message, 'true')

    else:
        output_message += 'No suitable entities were found.\n'
        output_message += errors

        siemplify.end(output_message, 'false')


if __name__ == "__main__":
    main()
