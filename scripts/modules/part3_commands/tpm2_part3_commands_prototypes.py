# -*- coding: utf-8 -*-

import settings
from modules.prototypes.tpm2_partx_prototype_file import PrototypeFile
from modules.file_handling import FileHandling
from modules import utils
from modules import data_structures
from modules.part3_commands import tpm2_part3_commands_prototypes_templates


class CommandPrototypeFile(PrototypeFile):

    # Extracts structures and modifiers
    # Parameters:
    # funcname
    # table_command
    # table_response
    # command_dispatcher
    def extract_structures_and_modifiers(self, funcname, table_command, table_response, command_dispatcher):

        in_table_params_found = False
        out_table_params_found = False
        handles = ""
        unmarshal = ""
        marshal = ""

        # only used if settings.ENABLE_TABLE_DRIVEN_DISPATCHER is True
        cdd_list_offsets = []
        cdd_list_types_in_handles = []
        cdd_list_types_in_parameters = []
        cdd_list_types_out_handles = []
        cdd_list_types_out_parameters = []
        #

        if table_command is not None:
            rows = table_command.rows[4:]  # remove TPM command header

            if rows:
                num = 0
                members = ""
                handles_list = []
                params_list = []
                modifier_handles_list = []
                modifier_params_list = []
                for row in rows:
                    in_table_params_found = True

                    old_type = row[0].strip().replace("+", "")
                    new_type = row[1].strip().replace("@", "")

                    # add member to input structure definition
                    members += tpm2_part3_commands_prototypes_templates.structure_member.safe_substitute(
                        OLD_TYPE=old_type,
                        NEW_TYPE=new_type
                    )

                    if utils.is_handle(row):
                        modifier_handles_list.append([self.name, new_type])
                        handles_list.append([funcname, row[0].strip(), new_type.strip(), num])

                        if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                            cdd_list_types_in_handles.append(row[0].strip())
                    else:
                        modifier_params_list.append([self.name, new_type])
                        params_list.append([funcname, row[0].strip(), new_type.strip(), num])
                        if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                            cdd_list_types_in_parameters.append(row[0].strip())

                        if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                            cdd_list_types_in_parameters += [cdd_list_types_in_handles[-1].replace("_H_", "_P_")]
                            cdd_list_types_in_handles = cdd_list_types_in_handles[:-1]

                    if settings.ENABLE_TABLE_DRIVEN_DISPATCHER and row is not rows[0]:
                        cdd_list_offsets.append(["In", new_type])

                    num += 1

                for h in modifier_handles_list:
                    self.modifiers.add_modifier_handle(h[0], h[1])
                for h in handles_list:
                    handles += command_dispatcher.create_command_dispatcher_unmarshal_handle(h[0], h[2], h[3])
                for p in modifier_params_list:
                    self.modifiers.add_modifier_param(p[0], p[1])
                for p in params_list:
                    unmarshal += command_dispatcher.create_command_dispatcher_unmarshal(p[0], p[1], p[2])

                # finalize response code modifiers
                self.modifiers.append("\n")

                # finalize input structure definition
                self.structure_in.content = tpm2_part3_commands_prototypes_templates.structure_in.safe_substitute(
                    MEMBERS=members[:-1],
                    NAME=self.name
                )

            if table_response is not None:
                rows = table_response.rows[4:]  # remove TPM command header
                if rows:
                    out_table_params_found = True
                    members = ""
                    for row in rows:

                        old_type = row[0].strip().replace("+", "")
                        new_type = row[1].strip().replace("@", "")

                        # add member to output structure definition
                        members += tpm2_part3_commands_prototypes_templates.structure_member.safe_substitute(
                            OLD_TYPE=old_type,
                            NEW_TYPE=new_type
                        )

                        if utils.is_handle(row) \
                                or "HMAC_Start" in funcname or "HashSequenceStart" in funcname\
                                or "ContextLoad" in funcname:  # handle table section
                            marshal += command_dispatcher.create_command_dispatcher_marshal_handle(funcname, old_type, new_type)
                            if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                                cdd_list_types_out_handles.append(row[0].strip())
                        else:
                            marshal += command_dispatcher.create_command_dispatcher_marshal(funcname, old_type, new_type)
                            if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                                cdd_list_types_out_parameters.append(row[0].strip())

                        if row is not rows[0]:
                            cdd_list_offsets.append(["Out", new_type])

                    # finalize output structure definition
                    self.structure_out.content += tpm2_part3_commands_prototypes_templates.structure_out.safe_substitute(
                        MEMBERS=members[:-1],
                        NAME=self.name
                    )
        if in_table_params_found or out_table_params_found:
            command_dispatcher.create_command_dispatcher_case(funcname,
                                                              in_table_params_found,
                                                              out_table_params_found,
                                                              handles,
                                                              unmarshal,
                                                              marshal)

    # Extracts prototype functions from given code blocks
    # Parameters:
    # code_blocks
    def extract_prototype_functions(self, code_blocks):
        text_p_prev = None
        add_to_prototype_file = False
        for element in code_blocks.elements:

            if not isinstance(element, data_structures.TPM2_Partx_CodeLine):
                continue

	    if settings.SPEC_VERSION_INT == 138 and "TPM2_Import" in element.string:
		element.string = element.string.strip()

            # add prototype line as long as line is part of the function signature
            if not element.string.startswith(" ") and element.string.endswith("(") \
                    and not text_p_prev.startswith("static"):
                add_to_prototype_file = True
                self.functions.append(text_p_prev + "\n")
                self.functions.append(element.string + "\n")
            elif add_to_prototype_file:
                if not element.string.strip() == "{":
                    self.functions.append(element.string)
                self.functions.append('\n')

            # stop adding
            if add_to_prototype_file and element.string.strip() == "{":
                add_to_prototype_file = False
                self.functions.content = self.functions.content[:-2] + ';\n'

            text_p_prev = element.string

    # Writes contents into file
    def write(self):
        # create name
        name = self.header_name.upper()
        if self.name.startswith("_"):
            name = self.header_name.upper()[:-1] + "FP_H_"   # replace "_" with "FP_H_"

        # IFDEF for command
        command_ifdef = ""
        if not self.name.startswith("_"):
            command_ifdef = tpm2_part3_commands_prototypes_templates.command_ifdef.safe_substitute(
                NAME=self.name
            )

        # Modifiers
        modifiers = ""
        if self.modifiers.content is not u'':
            modifiers= self.modifiers.content

        # Functions
        functions = self.functions.content

        # ENDIF for command
        command_endif = ""
        if not self.name.startswith("_"):
            command_endif = tpm2_part3_commands_prototypes_templates.command_endif.safe_substitute(
                NAME=self.name
            )

        # create file content
        content = tpm2_part3_commands_prototypes_templates.command_prototype_template.safe_substitute(
            COMMAND_IFDEF=command_ifdef,
            NAME=name,
            STRUCTURE_IN=self.structure_in.content,
            STRUCTURE_OUT=self.structure_out.content,
            MODIFIERS=modifiers,
            FUNCTIONS=functions,
            COMMAND_ENDIF=command_endif,
        )

        FileHandling.write_file(self.file_path, content)

