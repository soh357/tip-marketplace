from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from IPInfoManager import IPInfoManager
from SiemplifyUtils import dict_to_flat, flat_dict_to_csv, add_prefix_to_dict, convert_dict_to_json_result_dict
import json

ACTION_NAME = "IPInfo Get_IP_Information"
PROVIDER = 'IPInfo'
INTEGRATION_PREFIX = 'IPInfo'


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    conf = siemplify.get_configuration(PROVIDER)
    verify_ssl = conf.get('Verify SSL', 'false').lower() == 'true'
    ipinfo_manager = IPInfoManager(conf['API Root'], conf['Token'], verify_ssl)

    success_entities = []
    errors = []
    json_results = {}
    result_value = False

    ip_entities = [entity for entity in siemplify.target_entities if entity.entity_type == EntityTypes.ADDRESS]

    for entity in ip_entities:
        try:
            ip_information = ipinfo_manager.get_ip_information(entity.identifier)
            if ip_information:
                json_results[entity.identifier] = ip_information
                flat_info = dict_to_flat(ip_information)
                entity.additional_properties.update(add_prefix_to_dict(flat_info, INTEGRATION_PREFIX))
                entity.is_enriched = True
                siemplify.result.add_entity_table(entity.identifier, flat_dict_to_csv(flat_info))
                success_entities.append(entity)
                result_value = True
        except Exception as err:
            error_message = "Failed fetching information for {0}, ERROR: {1}".format(
                entity.identifier,
                err.message
            )
            siemplify.LOGGER.error(error_message)
            siemplify.LOGGER.exception(err)
            errors.append(error_message)

    siemplify.update_entities(success_entities)

    if success_entities:
        output_message = "Fetched IP information for: {0}".format(", ".join([entity.identifier for entity in
                                                                             success_entities]))
    else:
        output_message = "Mo information fetched for target entities."

    if errors:
        output_message = "{0}\n\nErrors:\n{1}".format(output_message, "\n".join(errors))

    siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_results))
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
