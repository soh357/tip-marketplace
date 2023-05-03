import sys
import json
from TIPCommon import extract_configuration_param, extract_action_param, construct_csv

from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_INPROGRESS
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from LastlineManager import LastlineManager
from consts import INTEGRATION_NAME, SUBMIT_URL
from datamodels import SubmissionTask
from exceptions import LastlineInvalidParamException, LastlinePermissionException, LastlineManyRequestsException, LastlineAuthenticationException


def start_operation(siemplify, manager, url: str, wait_for_report: bool):
    """
    If the action runs for the first time, this function will be called and will create a submission task.
    :param siemplify: {SiemplifyAction} Siemplify service
    :param manager: {LastlineManager} Lastline manager
    :param url: {str} The url to analyze
    :param wait_for_report: {bool} Decide if should wait to submission reports or not
    :return: (output_message, result_value, status)
    """
    status = EXECUTION_STATE_INPROGRESS
    output_message = ''

    siemplify.LOGGER.info(f"Submitting url to {INTEGRATION_NAME}: {url}")
    submission_task = manager.submit_url(url_for_analysis=url)
    siemplify.LOGGER.info(f"Successfully submitted url: {url}")

    if (wait_for_report and submission_task.data.raw_data.get('reports')) or not wait_for_report:
        return finish_operation(siemplify=siemplify,
                                submission_task=submission_task,
                                url=url,
                                wait_for_report=wait_for_report)

    else:
        result_value = json.dumps({
            'task_uuid': submission_task.data.task_uuid,
            'url': url,
        })
        output_message = f"Waiting for the analysis results for the url: {url}"

    return output_message, result_value, status


def query_operation_status(siemplify, manager, task_uuid: str, url: str, wait_for_report: bool):
    """
    Starting from the second time that the action will run, this function will be called and check if the submission
    task completed create a submission task.
    :param siemplify: {SiemplifyAction} Siemplify service
    :param manager: {LastlineManager} Lastline manager
    :param task_uuid: {str} Task identifier
    :param url: {str} The url to analyze
    :param wait_for_report: {bool} Decide if should wait to submission reports or not
    :return: (output_message, result_value, status)
    """

    siemplify.LOGGER.info(f"Checking the status of analysis task.")
    submission_task = manager.get_progress(uuid=task_uuid)
    siemplify.LOGGER.info(f"Successfully checked  the status of analysis task.")

    if submission_task.data.completed:
        completed_submission_task = manager.get_result(uuid=task_uuid)
        output_message, result_value, status = finish_operation(siemplify=siemplify,
                                                                submission_task=completed_submission_task,
                                                                url=url,
                                                                wait_for_report=wait_for_report)

    else:
        status = EXECUTION_STATE_INPROGRESS
        result_value = json.dumps({
            'task_uuid': task_uuid,
            'url': url,
        })
        output_message = f"Waiting for the analysis results for the url: {url}"

    return output_message, result_value, status


def finish_operation(siemplify, submission_task: SubmissionTask, url: str, wait_for_report: bool):
    """
    Finalizing results
    :param siemplify: {SiemplifyAction} Siemplify service
    :param submission_task: {SubmissionTask} Submission Task data model
    :param url: {str} Analyzed URL
    :param wait_for_report: {bool} Decide if should wait to submission reports or not
    :return: (output_message, result_value, status)
    """
    siemplify.LOGGER.info(f"Finalizing submission results for: {url}")

    # JSON
    json_results = submission_task.as_json()
    siemplify.result.add_result_json(json_results)

    # CSV and output message
    if wait_for_report:
        csv_table = [submission_task.as_csv()]
        csv_table_name = f"{url} Analysis Results"
        siemplify.result.add_data_table(csv_table_name, construct_csv(csv_table))
        output_message = f"Successfully fetched the analysis results for the url {url}"

    else:
        output_message = f"Successfully created analysis task for the url {url}"

    result_value = True
    status = EXECUTION_STATE_COMPLETED

    return output_message, result_value, status


@output_handler
def main(is_first_run):
    siemplify = SiemplifyAction()
    siemplify.script_name = "{} - {}".format(INTEGRATION_NAME, SUBMIT_URL)
    siemplify.LOGGER.info("================= Main - Param Init =================")

    api_root = extract_configuration_param(
        siemplify,
        provider_name=INTEGRATION_NAME,
        param_name='Api Root',
        is_mandatory=True,
        print_value=True
    )

    username = extract_configuration_param(
        siemplify,
        provider_name=INTEGRATION_NAME,
        param_name='Username',
        is_mandatory=True,
        print_value=True
    )

    password = extract_configuration_param(
        siemplify,
        provider_name=INTEGRATION_NAME,
        param_name='Password',
        is_mandatory=True,
    )

    verify_ssl = extract_configuration_param(
        siemplify,
        provider_name=INTEGRATION_NAME,
        param_name='Verify SSL',
        input_type=bool,
        default_value=True,
        is_mandatory=False,
        print_value=True
    )

    url = extract_action_param(siemplify,
                               param_name="URL For Analysis",
                               is_mandatory=False,
                               print_value=True)

    wait_for_report = extract_action_param(siemplify,
                                           param_name="Wait for the report?",
                                           is_mandatory=False,
                                           print_value=True,
                                           input_type=bool)

    mode = "Main" if is_first_run else {SUBMIT_URL}
    siemplify.LOGGER.info(f"----------------- {mode} - Started -----------------")

    try:
        manager = LastlineManager(api_root=api_root,
                                  username=username,
                                  password=password,
                                  verify_ssl=verify_ssl, )

        if is_first_run:
            output_message, result_value, status = start_operation(siemplify=siemplify,
                                                                   manager=manager,
                                                                   url=url,
                                                                   wait_for_report=wait_for_report)

        else:
            task_uuid = json.loads(siemplify.extract_action_param("additional_data")).get('task_uuid')
            url = json.loads(siemplify.extract_action_param("additional_data")).get('url')
            output_message, result_value, status = query_operation_status(siemplify=siemplify,
                                                                          manager=manager,
                                                                          task_uuid=task_uuid,
                                                                          url=url,
                                                                          wait_for_report=wait_for_report)

    except LastlineInvalidParamException as error:
        result_value = False
        status = EXECUTION_STATE_COMPLETED
        output_message = f'Failed to create analysis task because the provided url {url} is incorrect.'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(error)

    except (LastlinePermissionException, LastlineManyRequestsException) as error:
        result_value = False
        status = EXECUTION_STATE_COMPLETED
        output_message = f'Failed to create analysis task for the url {url}. Error is: {error}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(error)

    except LastlineAuthenticationException as error:
        result_value = False
        status = EXECUTION_STATE_FAILED
        output_message = f"Failed to connect to the {INTEGRATION_NAME} service with the provided account. Please " \
                         f"check your configuration. Error is: {error}"
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(error)

    except Exception as error:
        result_value = False
        status = EXECUTION_STATE_FAILED
        output_message = f'Failed to create analysis task for the url {url}. Error is: {error}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(error)

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(f"Status: {status}:")
    siemplify.LOGGER.info(f"Result Value: {result_value}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    is_first_run = len(sys.argv) < 3 or sys.argv[2] == 'True'
    main(is_first_run)
