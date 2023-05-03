from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
from CiscoFirepowerManager import CiscoFirepowerManager
from SiemplifyDataModel import EntityTypes

INTEGRATION_PROVIDER = 'CiscoFirepowerManagementCenter'


@output_handler
def main():

    siemplify = SiemplifyAction()
    conf = siemplify.get_configuration(INTEGRATION_PROVIDER)
    verify_ssl = str(conf.get('Verify SSL', 'false').lower()) == str(True).lower()
    cisco_firepower_manager = CiscoFirepowerManager(conf['API Root'],
                                                    conf['Username'],
                                                    conf['Password'],
                                                    verify_ssl)
    # Parameters.
    port_group_name = siemplify.parameters.get('Port Group Name')
    port = siemplify.parameters.get('Port')
    port_protocol = siemplify.parameters.get('Port Protocol')

    # Set script name.
    siemplify.script_name = 'CiscoFirepower_Block_Port'

    # Get url group object to pass to the block function.
    port_group_object = cisco_firepower_manager.get_port_group_object_by_name(port_group_name)

    result_value = cisco_firepower_manager.block_port(port_group_object,port_protocol, port)

    if result_value:
        output_message = 'Port {0} was blocked.'.format(port)
    else:
        output_message = 'No ports were blocked.'

    siemplify.end(output_message, result_value)


if __name__ == '__main__':
    main()
