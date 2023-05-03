from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import construct_csv
from PortnoxManager import PortnoxManager
import arrow


SCRIPT_NAME = "Portnox - GetDeviceHistory"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    conf = siemplify.get_configuration("Portnox")
    api_root = conf['Api Root']
    username = conf['Username']
    password = conf['Password']
    use_ssl = str(conf.get('Verify SSL', 'False')).lower() == 'true'
    portnox_manager = PortnoxManager(api_root, username, password, use_ssl)

    days_backwards = int(siemplify.parameters['Days Backwards'])
    from_timestamp = arrow.utcnow().shift(days=-days_backwards).isoformat()
    to_timestamp = arrow.utcnow().isoformat()
    enriched_entities = []

    for entity in siemplify.target_entities:
        try:
            device = None

            if entity.entity_type == EntityTypes.ADDRESS:
                device = portnox_manager.search_device('ip', entity.identifier)

            elif entity.entity_type == EntityTypes.MACADDRESS:
                device = portnox_manager.search_device('macAddress', entity.identifier)

            if device:
                device_id = device["id"]
                device_history = portnox_manager.get_device_history(
                    device_id,
                    from_timestamp,
                    to_timestamp)

                if device_history:
                    csv_output = construct_csv(device_history)

                    siemplify.result.add_entity_table(
                        '{} - Device History'.format(
                            entity.identifier),
                        csv_output)

                    enriched_entities.append(entity)

        except Exception as e:
            # An error occurred - skip entity and continue
            siemplify.LOGGER.error(
                "An error occurred on entity: {}.\n{}.".format(
                    entity.identifier, str(e)
                ))

    if enriched_entities:
        entities_names = [entity.identifier for entity in enriched_entities]

        output_message = 'Device history was found for the following entities:\n' + '\n'.join(
            entities_names)

        siemplify.update_entities(enriched_entities)

    else:
        output_message = 'No device history was found.'

    siemplify.end(output_message, 'true')


if __name__ == "__main__":
    main()
