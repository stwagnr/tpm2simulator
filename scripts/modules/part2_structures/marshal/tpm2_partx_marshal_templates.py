# -*- coding: utf-8 -*-

from string import Template
from textwrap import dedent

# This file contains templates for marshalling and unmarshalling functions for every type

########################################################################################################################
# TEMPLATES FOR EMTPY STRUCTURE                                                                                        #
########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

    Where:
        TYPE name of the data type or structure
        *target location in the TPM memory into which the data from **buffer is placed
        **buffer location in input buffer containing the most significant octet (MSO) of *target
        *size number of octets remaining in **buffer

    When the data is successfully unmarshaled, the called routine will return TPM_RC_SUCCESS.
    Otherwise, it will return a Format-One response code (see TPM 2.0 Part 2).
'''

TPMS_EMPTY_UNMARSHAL = dedent("""\
                        TPM_RC
                        TPMS_EMPTY_Unmarshal(
                            TPMS_EMPTY *target, BYTE **buffer, INT32  *size)
                        {
                            // unreferenced parameters (see Part 4: Unreferenced Parameter)
                            UNREFERENCED(target);
                            UNREFERENCED(buffer);
                            UNREFERENCED(size);
                            return TPM_RC_SUCCESS;      // return success
                        }

                        """)

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    UINT16 TYPE_Marshal(TYPE *source, BYTE **buffer, INT32 *size);

    Where:
        TYPE name of the data type or structure
        *source location in the TPM memory containing the value that is to be marshaled in to the designated
            buffer
        **buffer location in the output buffer where the first octet of the TYPE is to be placed
        *size number of octets remaining in **buffer. If size is a NULL pointer, then no data is marshaled and
            the routine will compute the size of the memory required to marshal the indicated type

    When the data is successfully marshaled, the called routine will return the number of octets marshaled
    into **buffer.
    If the data is successfully marshaled, *buffer is advanced point to the first octet of the next location in
    the output buffer and *size is reduced by the number of octets placed in the buffer.
'''
TPMS_EMPTY_MARSHAL = dedent("""\
                        UINT16
                        TPMS_EMPTY_Marshal(
                            TPMS_EMPTY *source, BYTE **buffer, INT32  *size)
                        {
                            // unreferenced parameters (see Part 4: Unreferenced Parameter)
                            UNREFERENCED(source);
                            UNREFERENCED(buffer);
                            UNREFERENCED(size);
                            return 0;                   // return zero
                        }

                        """)

########################################################################################################################

# Similar to TSS code,
Base_Type_Unmarshal_code = Template(dedent("""\
                            if((*size) < sizeof(${TYPE})) // if buffer size not sufficient
                                    return TPM_RC_INSUFFICIENT;  // return corresponding error code

                                *target = BYTE_ARRAY_TO_${TYPE}(*buffer);
                                *buffer += sizeof(${TYPE});
                                *size -= sizeof(${TYPE});
                        """))

# Similar to TSS code, rewritten to use less lines
Base_Type_Marshal_code = Template(dedent("""\
                        if (buffer != NULL)  // if buffer pointer is not a null pointer
                            {
                                pAssert ((size == NULL) || (((UINT32)*size) >= sizeof(${TYPE}))); // assert size of buffer is large enough

                                ${TYPE}_TO_BYTE_ARRAY(*source, *buffer);
                                *buffer += sizeof(${TYPE}); // adjust size of empty buffer
                                if (size != NULL)
                                {
                                    *size -= sizeof(${TYPE});
                                }

                            }
                            return sizeof(${TYPE});\
                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

    Where:
        TYPE name of the data type or structure
        *target location in the TPM memory into which the data from **buffer is placed
        **buffer location in input buffer containing the most significant octet (MSO) of *target
        *size number of octets remaining in **buffer

    When the data is successfully unmarshaled, the called routine will return TPM_RC_SUCCESS.
    Otherwise, it will return a Format-One response code (see TPM 2.0 Part 2).
'''

TYPE_Unmarshal_simple = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32 *size${FLAG})
                        {
                            ${CODE}
                            ${RETURN}
                        }

                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Array_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size, INT32 count);

    The generated code for an array uses a count-limited loop within which it calls the unmarshaling code
    for TYPE.
'''

TYPE_Marshal_simple = Template(dedent("""\
                        UINT16
                        ${TYPE}_Marshal(
                            ${TYPE} *source, BYTE **buffer, INT32 *size)
                        {
                            ${CODE}
                        }

                        """))

# Similar style as in TSS code
call_TYPE_unmarshal_struct = Template(dedent("""\
                        if (rc == TPM_RC_SUCCESS)
                            {
                                rc = ${TO_TYPE}_Unmarshal((${TO_TYPE}*)&target->${MEMBER}, buffer, size ${TO_MEMBER});
                            }
                    """))

# Similar style as in TSS code
call_TYPE_array_unmarshal_struct = Template(dedent("""\
                        if (rc == TPM_RC_SUCCESS)
                            {
                                rc = ${TO_TYPE}_Array_Unmarshal((${TO_TYPE}*)target->${MEMBER}, buffer, size ${TO_MEMBER});
                            }
                        """))

# Similar to TSS code
call_TYPE_marshal_struct = Template(dedent("""\
                    written += ${TO_TYPE}_Marshal((${TO_TYPE}*)&(source->${MEMBER}), buffer, size ${TO_MEMBER});
                    """))

# Similar to TSS code
call_TYPE_array_marshal_struct = Template(dedent("""\
                    written += ${TO_TYPE}_Array_Marshal((${TO_TYPE}*)(source->${MEMBER}), buffer, size ${TO_MEMBER});
                    """))

# Similar to TSS code
call_marshal_size = Template(dedent("""\
                    written += UINT16_Marshal(&written, &sizeField, size);
                    """))


comparison_check = Template(dedent("""\
                    if((target->${MEMBER}) ${SIGN} ${COMPARE_TO})
                            return ${RC_FAIL};
                    """))

size_zero_check = Template(dedent("""\
                    // if size is zero, then the structure is a zero buffer
                        if(target->${STRUCT}size == 0)
                            return ${RETURN};
                    """))

# Similar style as in TSS code
if_success_execute = Template(dedent("""\
                        
                        if (rc == TPM_RC_SUCCESS)
                            {
                                ${COMMAND}
                            }
                        """))

check_struct_size = "if(target->t.size != (startSize - *size)) return TPM_RC_SIZE;"

########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

    Where:
        TYPE name of the data type or structure
        *target location in the TPM memory into which the data from **buffer is placed
        **buffer location in input buffer containing the most significant octet (MSO) of *target
        *size number of octets remaining in **buffer

    When the data is successfully unmarshaled, the called routine will return TPM_RC_SUCCESS.
    Otherwise, it will return a Format-One response code (see TPM 2.0 Part 2).
'''

TYPE_Unmarshal_advanced = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32  *size)
                        {
                            TPM_RC rc;
                            rc = ${TO_TYPE}_Unmarshal((${TO_TYPE} *)target, buffer, size); // perform unmarshal

                            if(rc == TPM_RC_SUCCESS) // if unmarshalling succeeds
                            {
                                switch(*target)
                                {
                                    ${CASES}
                                        break;
                                    default :           // if target does not contain valid value
                                        rc = ${RC_FAIL};  // return fail
                                }
                            }
                            return rc;
                        }

                        """))


########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

'''

TYPE_Unmarshal_bits = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32  *size)
                        {
                            TPM_RC    rc;
                            rc = ${TO_TYPE}_Unmarshal(&target->val, buffer, size);

                            if(rc == TPM_RC_SUCCESS)
                                if(target->val & (${TO_TYPE})${RESERVED})
                                    rc = TPM_RC_RESERVED_BITS;

                            return rc;
                        }

                        """))


########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

'''

TYPE_Unmarshal_interface = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32  *size${FLAG})
                        {
                            TPM_RC    rc;
                            rc = ${TO_TYPE}_Unmarshal((${TO_TYPE} *)target, buffer, size);

                            if (rc == TPM_RC_SUCCESS) // if unmarshalling succeeds
                            {
                                switch (*target)
                                {   ${ALGS}
                                        break;
                                    ${CONDITION}
                                    default:
                                        ${CHECKS}
                                }
                            }
                            return rc;
                        }

                        """))


TYPE_Unmarshal_interface2 = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32   *size${FLAG})
                        {
                            TPM_RC    rc;
                            rc = ${TO_TYPE}_Unmarshal((${TO_TYPE} *)target, buffer, size);

                            if (rc == TPM_RC_SUCCESS) // if unmarshalling succeeds
                            {
                                ${CONDITION}
                                ${CHECKS}
                            }
                            return rc;
                        }

                        """))

interface_condition_caseif_template = Template(dedent("""\
                                    case ${COND}:
                                                    if (allowNull)
                                                        break;"""))
# Similar style as in TSS code
interface_condition_caseifnot_template = Template(dedent("""\
                                    case ${COND}:
                                                    if (!allowNull)
                                                        rc = ${RC_FAIL};
                                                    break;"""))
# Similar style as in TSS code
interface_condition_if_template = Template(dedent("""\
                                    if (*target == ${COND})
                                            {
                                                if (!allowNull)
                                                    rc = ${RC_FAIL};
                                            }
                                            else"""))

ifdef_case_template = Template(dedent("""
                        #ifdef    ${CASE}
                                    case ${CASE}:
                        #endif // ${CASE}"""))

# Similar to TSS code
target_bounds_check_template = Template("((*target < ${LEFT_BOUNDARY}) || (*target > ${RIGHT_BOUNDARY}))")

########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size, UINT32 selector);

    where:
        TYPE name of the union type or structure
        *target location in the TPM memory into which the data from **buffer is placed
        **buffer location in input buffer containing the most significant octet (MSO) of *target
        *size number of octets remaining in **buffer
        selector union selector that determines what will be unmarshaled into *target


'''

TYPE_Unmarshal_union = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32 *size, UINT32 selector)
                        {
                            switch (selector)
                            {
                        ${ALGS}
                        ${CASES}
                            }
                            return TPM_RC_SELECTOR;
                        }

                        """))



'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Marshal(TYPE *target, BYTE **buffer, INT32 *size, UINT32 selector);

'''

TYPE_Marshal_union = Template(dedent("""\
                        UINT16
                        ${TYPE}_Marshal(
                            ${TYPE} *source, BYTE **buffer, INT32 *size, UINT32 selector
                            )
                        {
                            switch (selector)
                            {
                        ${ALGS}
                        ${CASES}
                            }
                            return 0;
                        }

                        """))

return_type_unmarshal = Template(
    "            return ${TO_TYPE}_Unmarshal((${TO_TYPE}*)&(target->${MEMBER}), buffer, size ${TO_MEMBER});\n")
return_array_unmarshal = Template(
    "            return ${TO_TYPE}_Array_Unmarshal((${TO_TYPE}*)(target->${MEMBER}), buffer, size ${TO_MEMBER});\n")

return_type_marshal = Template(
    "            return ${TO_TYPE}_Marshal((${TO_TYPE}*)&(source->${MEMBER}), buffer, size ${TO_MEMBER});\n")
return_array_marshal = Template(
    "            return ${TO_TYPE}_Array_Marshal((${TO_TYPE}*)(source->${MEMBER}), buffer, size ${TO_MEMBER});\n")


########################################################################################################################

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Array_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size,INT32 count);

    The generated code for an array uses a count-limited loop within which it calls the unmarshaling code
    for TYPE.

For BYTE, we generate a simple memcpy operation and then set 'buffer' and 'size' accordingly.
'''

BYTE_Array_Unmarshal = Template(dedent("""\
                        #include    <string.h>
                        TPM_RC
                        ${TYPE}_Array_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32 *size, INT32  count)
                        {
                            if(*size < count)       // if buffer size not sufficient
                                return TPM_RC_INSUFFICIENT;   // return corresponding error code

                            memcpy(target, *buffer, count);   // copy the given amount of bytes from buffer to target
                            *buffer += count;           // set the buffer pointer to the empty part of the buffer
                            *size -= count;             // adjust size of empty buffer
                            return TPM_RC_SUCCESS;      // return success
                        }

                        """))

'''
The following template is based on Part 4 (Section "Marshaling Code Function Prototypes"):

    UINT16 TYPE_Array_Marshal(TYPE *source, BYTE **buffer, INT32 *size, INT32 count);

    The generated code for an array uses a count-limited loop within which it calls the marshaling code
    for TYPE.

For BYTE, we generate a simple memcpy operation and then set 'buffer' and 'size' accordingly.
'''

BYTE_Array_Marshal = Template(dedent("""\
                        UINT16
                        ${TYPE}_Array_Marshal(
                            ${TYPE} *source, BYTE **buffer, INT32 *size, INT32  count)
                        {
                            if (buffer != 0) // if buffer pointer is not a nullpointer
                            {
                                if ((size == 0) || ((*size -= count) >= 0))  // if size of buffer is large enough
                                {
                                    memcpy(*buffer, source, count); // copy given amount of bytes from source to buffer
                                    *buffer += count;       // set buffer pointer to the empty part of the buffer
                                }
                                pAssert(size == 0 || (*size >= 0));
                            }
                            pAssert(count < UINT16_MAX);
                            return ((UINT16)count);
                        }

                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Array_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size,INT32 count);

    The generated code for an array uses a count-limited loop within which it calls the unmarshaling code
    for TYPE.
'''

TYPE_Array_Unmarshal = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Array_Unmarshal(
                            ${TYPE} *target, BYTE **buffer, INT32 *size${FLAG1}, INT32  count)
                        {
                            TPM_RC    rc;
                            UINT32 i;
                            for(i = 0; i < count; i++) { // loop to process given amount of values
                                rc = ${TYPE}_Unmarshal(&target[i], buffer, size${FLAG2});
                                if(rc != TPM_RC_SUCCESS) // if unmarshalling fails
                                    return rc;  // return error code
                            }
                            return TPM_RC_SUCCESS;
                        }

                        """))

'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Array_Marshal(TYPE *source, BYTE **buffer, INT32 *size, INT32 count);

    The generated code for an array uses a count-limited loop within which it calls the marshaling code
    for TYPE.
'''

TYPE_Array_Marshal = Template(dedent("""\
                        UINT16
                        ${TYPE}_Array_Marshal(
                            ${TYPE} *source, BYTE **buffer, INT32 *size, INT32  count)
                        {
                            UINT16 rc = 0;
                            UINT32 i;
                            for(i = 0; i < count; i++)   // loop to process given amount of values
                            {
                                rc = (UINT16)(rc + ${TYPE}_Marshal(&source[i], buffer, size));
                            }
                            return rc;
                        }

                        """))


########################################################################################################################
#                                                                                                                      #
# TEMPLATES FOR FILE PROTOTYPES                                                                                        #
#                                                                                                                      #
########################################################################################################################

# UNMARSHAL # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


'''
    The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

        TPM_RC TYPE_Array_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size, INT32 count);
'''

TYPE_Array_Unmarshal_fp = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Array_Unmarshal(${TYPE} *target, BYTE **buffer, INT32 *size${FLAG}, INT32 count);
                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

'''

TYPE_Unmarshal_simple_fp = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(${TYPE} *target, BYTE **buffer, INT32 *size${FLAG});
                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size);

If there already exists a unmarshal function for the base type (TO_TYPE), a #define is used.
'''

TYPE_Unmarshal_structure_fp_define = Template(dedent("""\
                        #define ${TYPE}_Unmarshal(target, buffer, size) \\
                            ${TO_TYPE}_Unmarshal((${TO_TYPE} *)${VAR}, buffer, size${FLAG})
                        """))

'''
The following template is based on Part 4 (Section "Unmarshaling Code Prototype"):

    TPM_RC TYPE_Unmarshal(TYPE *target, BYTE **buffer, INT32 *size, UINT32 selector);

'''

TYPE_Unmarshal_union_fp = Template(dedent("""\
                        TPM_RC
                        ${TYPE}_Unmarshal(${TYPE} *target, BYTE **buffer, INT32 *size, UINT32 selector);
                        """))

# MARSHAL # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Array_Marshal(TYPE *source, BYTE **buffer, INT32 *size, INT32 count);

'''

TYPE_Array_Marshal_fp = Template(dedent("""\
                        UINT16
                        ${TYPE}_Array_Marshal(${TYPE} *source, BYTE **buffer, INT32 *size, INT32 count);

                        """))

'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Marshal(TYPE *source, BYTE **buffer, INT32 *size);

'''

TYPE_Marshal_simple_fp = Template(dedent("""\
                        UINT16
                        ${TYPE}_Marshal(${TYPE} *source, BYTE **buffer, INT32 *size);

                        """))

'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Marshal(TYPE *source, BYTE **buffer, INT32 *size);

If there already exists a marshal function for the base type (TO_TYPE), a #define is used.
'''

TYPE_Marshal_simple_fp_define = Template(dedent("""\
                        #define ${TYPE}_Marshal(source, buffer, size) \\
                            ${TO_TYPE}_Marshal((${TO_TYPE} *)${VAR}, buffer, size)

                        """))

'''
The following template is based on Part 4 (Section "Marshaling Code Prototype"):

    UINT16 TYPE_Marshal(TYPE *target, BYTE **buffer, INT32 *size, UINT32 selector);

'''

TYPE_Marshal_union_fp = Template(dedent("""\
                        UINT16
                        ${TYPE}_Marshal(${TYPE} *source, BYTE **buffer, INT32 *size, UINT32 selector);

                        """))


RETURN_SUCCESS = "return TPM_RC_SUCCESS;"

IFDEF_ALG = "#ifdef    TPM_ALG_{0}\n"
ENDIF_ALG = "#endif // TPM_ALG_{0}\n\n"


COMMENT_TYPE_Unmarshal_defined = "//   {0}_Unmarshal changed to #define\n"
COMMENT_TYPE_Marshal_defined = "//   {0}_Marshal changed to #define\n"

COMMENT_TYPE_Unmarshal_not_req = "//   {0}_Unmarshal not required\n"
COMMENT_TYPE_Marshal_not_req = "//   {0}_Marshal not required\n"

COMMENT_TYPE_Array_Unmarshal_not_req = "// {0}_Array_Unmarshal not required\n"
COMMENT_TYPE_Array_Marshal_not_req = "// {0}_Array_Marshal not required\n"

COMMENT_Array_Un_Marshal_TYPE = "// Array Marshal/Unmarshal for {0}\n"
