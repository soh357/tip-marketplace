from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes
from SiemplifyAction import SiemplifyAction
from WildfireManager import WildfireManager
import base64

@output_handler
def main():
    siemplify = SiemplifyAction()
    conf = siemplify.get_configuration('Wildfire')
    api_key = conf['Api Key']

    errors = ""
    enriched_entities = []

    # Connect to Wildfire
    wildfire_manager = WildfireManager(api_key)

    for entity in siemplify.target_entities:
        if entity.entity_type == EntityTypes.FILEHASH:
            if len(entity.identifier) == 32 or len(entity.identifier) == 64:
                try:
                    # Hash is md5 or sha256
                    pcap_file = wildfire_manager.get_pcap(entity.identifier)
                    siemplify.result.add_entity_attachment(
                        entity.identifier,
                        pcap_file['filename'],
                        base64.b64encode(pcap_file['content'])
                    )
                    enriched_entities.append(entity)

                except Exception as e:
                    errors += e.message + "\n"

    if enriched_entities:
        entities_names = [entity.identifier for entity in enriched_entities]

        output_message = 'Report was saved for the following entities:\n' + '\n'.join(
            entities_names)
        output_message += errors

    else:
        output_message = 'No reports were downloaded.\n'
        output_message += errors

    siemplify.end(output_message, 'true')


if __name__ == "__main__":
    main()
