from TIPCommon import extract_configuration_param, extract_action_param, construct_csv
from TIPCommon import flat_dict_to_csv

import consts
import utils
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from Siemplify import InsightSeverity, InsightType
from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from ThreatFuseManager import ThreatFuseManager
from exceptions import ThreatFuseValidationException, ThreatFuseInvalidCredentialsException, \
    ThreatFuseStatusCodeException

SCRIPT_NAME = "Enrich Entities"
SUPPORTED_ENTITIES = (EntityTypes.FILEHASH, EntityTypes.ADDRESS, EntityTypes.URL, EntityTypes.USER)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "{} - {}".format(consts.INTEGRATION_NAME, SCRIPT_NAME)
    siemplify.LOGGER.info("================= Main - Param Init =================")

    web_root = extract_configuration_param(
        siemplify,
        provider_name=consts.INTEGRATION_NAME,
        param_name='Web Root',
        is_mandatory=True,
        print_value=True
    )

    api_root = extract_configuration_param(
        siemplify,
        provider_name=consts.INTEGRATION_NAME,
        param_name='API Root',
        is_mandatory=True,
        print_value=True
    )

    email_address = extract_configuration_param(
        siemplify,
        provider_name=consts.INTEGRATION_NAME,
        param_name='Email Address',
        is_mandatory=True
    )

    api_key = extract_configuration_param(
        siemplify,
        provider_name=consts.INTEGRATION_NAME,
        param_name='API Key',
        is_mandatory=True,
    )

    verify_ssl = extract_configuration_param(
        siemplify,
        provider_name=consts.INTEGRATION_NAME,
        param_name='Verify SSL',
        input_type=bool,
        is_mandatory=True,
        print_value=True
    )

    severity_threshold = extract_action_param(siemplify, param_name="Severity Threshold", is_mandatory=True,
                                              print_value=True)
    confidence_threshold = extract_action_param(siemplify, param_name="Confidence Threshold", is_mandatory=True,
                                                input_type=int, print_value=True)
    ignore_false_positive = extract_action_param(siemplify, param_name="Ignore False Positive Status",
                                                 is_mandatory=False, input_type=bool, print_value=True,
                                                 default_value=False)
    add_threat_type_to_case = extract_action_param(siemplify, param_name="Add Threat Type To Case", is_mandatory=False,
                                                   input_type=bool, print_value=True, default_value=False)

    create_insight = extract_action_param(siemplify, param_name="Create Insight", is_mandatory=False,
                                          input_type=bool, print_value=True, default_value=False)

    suspicious_insight_only = extract_action_param(siemplify, param_name="Only Suspicious Entity Insight",
                                                   is_mandatory=False,
                                                   input_type=bool, print_value=True, default_value=False)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    supported_entities = []  # list of supported entities
    indicators = []  # list of found indicators
    enriched_entities = []
    failed_entities = []

    status = EXECUTION_STATE_COMPLETED
    json_results = {
        "results": {},
        "is_risky": False
    }
    result_value = "false"
    output_message = ""

    try:
        if confidence_threshold > consts.MAX_CONFIDENCE or confidence_threshold < consts.MIN_CONFIDENCE:
            raise ThreatFuseValidationException(
                f"Confidence Threshold' value should be in range from {consts.MIN_CONFIDENCE} to {consts.MAX_CONFIDENCE}")

        if severity_threshold not in consts.SEVERITIES:
            raise ThreatFuseValidationException(
                f"Severity Threshold' value should be one of {consts.SEVERITIES.keys()}")

        # translate to numeric severity
        numeric_severity_threshold = consts.SEVERITIES_ORDER[consts.SEVERITIES[severity_threshold]]

        manager = ThreatFuseManager(
            web_root=web_root,
            api_root=api_root,
            api_key=api_key,
            email_address=email_address,
            verify_ssl=verify_ssl
        )

        for entity in siemplify.target_entities:
            if entity.entity_type not in SUPPORTED_ENTITIES:
                siemplify.LOGGER.info("Entity {} is of unsupported type. Skipping.".format(entity.identifier))
                continue

            if consts.SPACE_CHARACTER in entity.identifier.strip():
                siemplify.LOGGER.info(
                    "Entity {} contains a ' ' character (space), which is not supported for the action's "
                    "supported entities.".format(entity.identifier))
                continue

            supported_entities.append(entity)

        siemplify.LOGGER.info(
            f"Supported entities are: {', '.join([entity.identifier for entity in supported_entities])}")

        if supported_entities:
            try:
                siemplify.LOGGER.info(f"Retrieving indicators.")

                # Get indicators for entities
                indicators = manager.get_indicators(entities=[entity.identifier.strip() for entity in supported_entities])

            except ThreatFuseInvalidCredentialsException as e:
                raise e

            except ThreatFuseStatusCodeException as e:
                siemplify.LOGGER.error(f"Failed to get indicators.")
                siemplify.LOGGER.exception(e)

        else:
            siemplify.LOGGER.info("No supported entities found.")

        if indicators:  # check if retrieved indicators
            # Map each entity to its indicators
            indicator_groups = manager.parser.match_entity_to_indicators(indicators, supported_entities)

            for indicator_group in indicator_groups:
                try:
                    # Process each indicator group separately
                    siemplify.LOGGER.info(f"Processing indicators of entity {indicator_group.entity.identifier}")
                    is_suspicious = False

                    if not indicator_group.indicators:
                        siemplify.LOGGER.info(
                            f"No indicators were found for entity {indicator_group.entity.identifier}. Skipping.")
                        failed_entities.append(indicator_group.entity)
                        continue

                    indicator_group.entity.additional_properties.update(indicator_group.as_enrichment())
                    indicator_group.entity.is_enriched = True
                    siemplify.result.add_entity_table(indicator_group.entity.identifier,
                                                      flat_dict_to_csv(indicator_group.as_csv())
                                                      )
                    json_results["results"][indicator_group.entity.identifier] = [indicator.as_json() for indicator in
                                                                                  indicator_group.indicators]
                    enriched_entities.append(indicator_group.entity)

                    siemplify.LOGGER.info(
                        f"Successfully enriched entity {indicator_group.entity.identifier} with indicators data.")

                    if indicator_group.is_false_positive and ignore_false_positive:
                        siemplify.LOGGER.info(
                            f"Latest indicator for entity {indicator_group.entity.identifier} is false positive. "
                            f"Entity won't be checked if suspicious."
                        )

                    else:
                        if indicator_group.numeric_severity >= numeric_severity_threshold and \
                                indicator_group.confidence >= confidence_threshold:
                            siemplify.LOGGER.info(
                                f"Severity and confidence passed threshold. "
                                f"Marking {indicator_group.entity.identifier} as suspicious."
                            )
                            indicator_group.entity.is_suspicious = True
                            is_suspicious = True
                            json_results["is_risky"] = True

                    siemplify.LOGGER.info(f"Fetching analysis links for entity {indicator_group.entity.identifier}")
                    analysis_links = manager.get_analysis_links(indicator_group.entity.identifier)

                    siemplify.LOGGER.info(f"Found {len(analysis_links)} analysis links.")

                    if analysis_links:
                        siemplify.result.add_data_table(
                            f"Related Analysis Links: {indicator_group.entity.identifier}",
                            construct_csv([link.as_csv() for link in analysis_links])
                        )

                    if add_threat_type_to_case:
                        siemplify.LOGGER.info(
                            f"Adding threat types of the indicators of {indicator_group.entity.identifier} as tags to case.")
                        for indicator in indicator_group.indicators:
                            siemplify.add_tag(indicator.threat_type)

                    if create_insight and (not suspicious_insight_only or is_suspicious):
                        try:
                            if indicator_group.entity.entity_type == EntityTypes.ADDRESS:
                                siemplify.LOGGER.info(f"Fetching intel details for {indicator_group.entity.identifier}")
                                intel_details = manager.get_intel_details(type=indicator_group.latest_indicator.type,
                                                                          value=indicator_group.entity.identifier)

                                siemplify.LOGGER.info(f"Adding insight for entity {indicator_group.entity.identifier}")
                                siemplify.create_case_insight(
                                    triggered_by=consts.INTEGRATION_IDENTIFIER,
                                    title="IP Details",
                                    content=indicator_group.as_ip_insight(intel_details),
                                    entity_identifier=indicator_group.entity.identifier,
                                    severity=InsightSeverity.INFO,
                                    insight_type=InsightType.Entity,
                                )

                            elif indicator_group.entity.entity_type == EntityTypes.URL:
                                siemplify.LOGGER.info(
                                    f"Fetching intel details for {indicator_group.entity.identifier} {indicator_group.latest_indicator.type}")
                                intel_details = manager.get_intel_details(type=indicator_group.latest_indicator.type,
                                                                          value=indicator_group.entity.identifier)

                                siemplify.LOGGER.info(f"Adding insight for entity {indicator_group.entity.identifier}")

                                if indicator_group.latest_indicator.type == consts.URL_INDICATOR_TYPE:
                                    # Indicator is of type URL
                                    siemplify.create_case_insight(
                                        triggered_by=consts.INTEGRATION_IDENTIFIER,
                                        title="URL Details",
                                        content=indicator_group.as_url_insight(intel_details),
                                        entity_identifier=indicator_group.entity.identifier,
                                        severity=InsightSeverity.INFO,
                                        insight_type=InsightType.Entity,
                                    )

                                else:
                                    # Indicator is of type domain
                                    siemplify.create_case_insight(
                                        triggered_by=consts.INTEGRATION_IDENTIFIER,
                                        title="Domain Details",
                                        content=indicator_group.as_domain_insight(intel_details),
                                        entity_identifier=indicator_group.entity.identifier,
                                        severity=InsightSeverity.INFO,
                                        insight_type=InsightType.Entity,
                                    )

                            elif indicator_group.entity.entity_type == EntityTypes.FILEHASH:
                                siemplify.LOGGER.info(f"Adding insight for entity {indicator_group.entity.identifier}")
                                siemplify.create_case_insight(
                                    triggered_by=consts.INTEGRATION_IDENTIFIER,
                                    title="Hash Details",
                                    content=indicator_group.as_hash_insight(),
                                    entity_identifier=indicator_group.entity.identifier,
                                    severity=InsightSeverity.INFO,
                                    insight_type=InsightType.Entity,
                                )

                            else:
                                # Entity is an email address
                                siemplify.LOGGER.info(f"Adding insight for entity {indicator_group.entity.identifier}")
                                siemplify.create_case_insight(
                                    triggered_by=consts.INTEGRATION_IDENTIFIER,
                                    title="Email Address Details",
                                    content=indicator_group.as_email_insight(),
                                    entity_identifier=indicator_group.entity.identifier,
                                    severity=InsightSeverity.INFO,
                                    insight_type=InsightType.Entity,
                                )

                        except Exception as e:
                            siemplify.LOGGER.error(
                                f"Failed to add insight for entity {indicator_group.entity.identifier}")
                            siemplify.LOGGER.exception(e)

                except Exception as e:
                    siemplify.LOGGER.error(f"An error occurred on entity {indicator_group.entity.identifier}")
                    siemplify.LOGGER.exception(e)
                    failed_entities.append(indicator_group.entity)

        else:
            siemplify.LOGGER.info("No indicators were found.")

        if enriched_entities:
            output_message += 'Successfully enriched the following entities using {}: \n{}'.format(
                consts.INTEGRATION_NAME,
                '\n'.join([entity.identifier for entity in enriched_entities]))
            siemplify.update_entities(enriched_entities)
            result_value = "true"

            if failed_entities:
                output_message += '\n\nAction was not able to enrich the following entities using {}: \n{}\n'.format(
                    consts.INTEGRATION_NAME,
                    '\n'.join([entity.identifier for entity in failed_entities]))

        else:
            siemplify.LOGGER.info('\n No entities were enriched.')
            output_message = 'No entities were enriched.'

    except ThreatFuseValidationException as error:
        siemplify.LOGGER.error(error)
        siemplify.LOGGER.exception(error)
        status = EXECUTION_STATE_FAILED
        output_message = f"{error}"

    except Exception as error:
        siemplify.LOGGER.error(f"Error executing action \"{SCRIPT_NAME}\". Reason: {error}")
        siemplify.LOGGER.exception(error)
        status = EXECUTION_STATE_FAILED
        output_message = f"Error executing action \"{SCRIPT_NAME}\". Reason: {error}"

    json_results["results"] = convert_dict_to_json_result_dict(json_results["results"])
    siemplify.result.add_result_json(json_results)
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Status: {}:".format(status))
    siemplify.LOGGER.info("Result Value: {}".format(result_value))
    siemplify.LOGGER.info("Output Message: {}".format(output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
