from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes
from FileOperationManager import FileOperationManager
from SiemplifyAction import *


@output_handler
def main():
    siemplify = SiemplifyAction()
    file_manager = FileOperationManager()
    server_ip = siemplify.parameters['server_ip']
    username = siemplify.parameters['username']
    password = siemplify.parameters['password']
    source_folder = siemplify.parameters['source_folder']
    file_filter = siemplify.parameters['file_filter']
    output_folder = siemplify.parameters['output_folder']
    zip_file_path = file_manager.zip_over_ssh_linux(server_ip, username, password, source_folder,
                                                 file_filter, output_folder)

    output_message = "Successfully created {0}".format(zip_file_path)
    siemplify.end(output_message, zip_file_path)


if __name__ == '__main__':
    main()
