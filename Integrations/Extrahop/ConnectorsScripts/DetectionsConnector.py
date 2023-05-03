from EnvironmentCommon import GetEnvironmentCommonFactory
from SiemplifyUtils import output_handler
from SiemplifyConnectors import SiemplifyConnectorExecution
from TIPCommon import (
    extract_connector_param,
    read_ids,
    is_approaching_timeout,
    pass_whitelist_filter,
    save_timestamp,
    get_last_success_time,
    UNIX_FORMAT,
    is_overflowed,
    unix_now,
    write_ids_with_timestamp
)
from constants import (
    CONNECTOR_NAME,
    DEFAULT_LIMIT,
    DEFAULT_TIME_FRAME,
    DEVICE_OBJECT_TYPE
)
from UtilsManager import pass_severity_filter
from ExtrahopManager import ExtrahopManager
from SiemplifyConnectorsDataModel import AlertInfo
import sys


connector_starting_time = unix_now()


@output_handler
def main(is_test_run):
    siemplify = SiemplifyConnectorExecution()
    siemplify.script_name = CONNECTOR_NAME
    processed_alerts = []

    if is_test_run:
        siemplify.LOGGER.info("***** This is an \"IDE Play Button\"\\\"Run Connector once\" test run ******")

    siemplify.LOGGER.info("------------------- Main - Param Init -------------------")

    api_root = extract_connector_param(siemplify, param_name="API Root", is_mandatory=True, print_value=True)
    client_id = extract_connector_param(siemplify, param_name="Client ID", is_mandatory=True, print_value=True)
    client_secret = extract_connector_param(siemplify, param_name="Client Secret", is_mandatory=True)
    verify_ssl = extract_connector_param(siemplify, param_name="Verify SSL", is_mandatory=True, input_type=bool,
                                         print_value=True)

    environment_field_name = extract_connector_param(siemplify, param_name="Environment Field Name", print_value=True)
    environment_regex_pattern = extract_connector_param(siemplify, param_name="Environment Regex Pattern",
                                                        print_value=True)

    script_timeout = extract_connector_param(siemplify, param_name="PythonProcessTimeout", is_mandatory=True,
                                             input_type=int, print_value=True)
    lowest_risk_to_fetch = extract_connector_param(siemplify, param_name="Lowest Risk Score To Fetch", input_type=int,
                                                   print_value=True)
    hours_backwards = extract_connector_param(siemplify, param_name="Max Hours Backwards",
                                              input_type=int, default_value=DEFAULT_TIME_FRAME, print_value=True)
    fetch_limit = extract_connector_param(siemplify, param_name="Max Detections To Fetch", input_type=int,
                                          default_value=DEFAULT_LIMIT, print_value=True)
    whitelist_as_a_blacklist = extract_connector_param(siemplify, "Use whitelist as a blacklist", is_mandatory=True,
                                                       input_type=bool, print_value=True)
    device_product_field = extract_connector_param(siemplify, "DeviceProductField", is_mandatory=True)

    try:
        siemplify.LOGGER.info("------------------- Main - Started -------------------")

        if hours_backwards < 1:
            siemplify.LOGGER.info(f"Max Hours Backwards must be greater than zero. The default value {DEFAULT_TIME_FRAME} "
                                  f"will be used")
            hours_backwards = DEFAULT_TIME_FRAME

        if fetch_limit < 1:
            siemplify.LOGGER.info(f"Max Detections To Fetch must be greater than zero. The default value {DEFAULT_LIMIT} "
                                  f"will be used")
            fetch_limit = DEFAULT_LIMIT

        if lowest_risk_to_fetch and (lowest_risk_to_fetch < 0 or lowest_risk_to_fetch > 100):
            raise Exception(f"Invalid value given for Lowest Risk Score To Fetch parameter. "
                            f"Value should be between 0 and 100. ")

        # Read already existing alerts ids
        existing_ids = read_ids(siemplify, default_value_to_return={})
        siemplify.LOGGER.info(f"Successfully loaded {len(existing_ids)} existing alerts from ids file")

        manager = ExtrahopManager(api_root=api_root, client_id=client_id, client_secret=client_secret,
                                  verify_ssl=verify_ssl, siemplify=siemplify)

        last_success_time = get_last_success_time(siemplify=siemplify,
                                                  offset_with_metric={"hours": hours_backwards},
                                                  time_format=UNIX_FORMAT)

        fetched_alerts = []

        filtered_alerts = manager.get_detections(
            existing_ids=existing_ids,
            limit=fetch_limit,
            start_timestamp=last_success_time
        )

        siemplify.LOGGER.info(f"Fetched {len(filtered_alerts)} alerts")

        if is_test_run:
            siemplify.LOGGER.info("This is a TEST run. Only 1 alert will be processed.")
            filtered_alerts = filtered_alerts[:1]

        for alert in filtered_alerts:
            try:
                if is_approaching_timeout(python_process_timeout=script_timeout,
                                          connector_starting_time=connector_starting_time):
                    siemplify.LOGGER.info("Timeout is approaching. Connector will gracefully exit")
                    break

                if len(processed_alerts) >= fetch_limit:
                    # Provide slicing for the alerts amount.
                    siemplify.LOGGER.info(
                        "Reached max number of alerts cycle. No more alerts will be processed in this cycle."
                    )
                    break

                siemplify.LOGGER.info(f"Started processing alert {alert.id}")

                # Update existing alerts
                existing_ids.update({str(alert.id): len(alert.participants)})
                fetched_alerts.append(alert)

                if not pass_filters(siemplify, whitelist_as_a_blacklist, alert, "type", lowest_risk_to_fetch):
                    continue

                for participant in alert.participants:
                    if participant.get("object_type", "") == DEVICE_OBJECT_TYPE:
                        alert.devices.append(manager.get_device_details(device_id=participant.get("object_id")))

                environment_common = GetEnvironmentCommonFactory.create_environment_manager(
                    siemplify=siemplify,
                    environment_field_name=environment_field_name,
                    environment_regex_pattern=environment_regex_pattern
                )
                alert_info = alert.get_alert_info(
                    alert_info=AlertInfo(),
                    environment_common=environment_common,
                    device_product_field=device_product_field
                )

                if is_overflowed(siemplify, alert_info, is_test_run):
                    siemplify.LOGGER.info(
                        f"{alert_info.rule_generator}-{alert_info.ticket_id}-{alert_info.environment}"
                        f"-{alert_info.device_product} found as overflow alert. Skipping...")
                    # If is overflowed we should skip
                    continue

                processed_alerts.append(alert_info)
                siemplify.LOGGER.info(f"Alert {alert.id} was created.")

            except Exception as e:
                siemplify.LOGGER.error(f"Failed to process alert {alert.id}")
                siemplify.LOGGER.exception(e)

                if is_test_run:
                    raise

            siemplify.LOGGER.info(f"Finished processing alert {alert.id}")

        if not is_test_run:
            siemplify.LOGGER.info("Saving existing ids.")
            write_ids_with_timestamp(siemplify, existing_ids)
            save_timestamp(siemplify=siemplify, alerts=fetched_alerts, timestamp_key="update_time")

    except Exception as e:
        siemplify.LOGGER.error(f"Got exception on main handler. Error: {e}")
        siemplify.LOGGER.exception(e)

        if is_test_run:
            raise

    siemplify.LOGGER.info(f"Created total of {len(processed_alerts)} cases")
    siemplify.LOGGER.info("------------------- Main - Finished -------------------")
    siemplify.return_package(processed_alerts)


def pass_filters(siemplify, whitelist_as_a_blacklist, alert, model_key, lowest_severity_to_fetch):
    # All alert filters should be checked here
    if not pass_whitelist_filter(siemplify, whitelist_as_a_blacklist, alert, model_key):
        return False

    if not pass_severity_filter(siemplify, alert, lowest_severity_to_fetch):
        return False

    return True


if __name__ == "__main__":
    # Connectors are run in iterations. The interval is configurable from the ConnectorsScreen UI.
    is_test = not (len(sys.argv) < 2 or sys.argv[1] == "True")
    main(is_test)
