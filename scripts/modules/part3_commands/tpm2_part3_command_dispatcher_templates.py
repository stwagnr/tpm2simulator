# -*- coding: utf-8 -*-

from string import Template

# This file contains templates used for generating the command dispatcher code

command_dispatcher_template = Template("""\
// Includes based on
#include    "InternalRoutines.h"                                    // include basic header files
#include    "Commands.h"                                            // include prototype files
#include    "SessionProcess_fp.h"                                   // Spec. Version 01.19+

#ifndef TABLE_DRIVEN_DISPATCH //%                                   // Spec. Version 01.19+

// This function is based on Part 4, Section "Main", CommandDispatcher():
// ----------------------------------------------------------------------
// CommandDispatcher() performs the following operations:
// * unmarshals command parameters from the input buffer;
// * invokes the function that performs the command actions;
// * marshals the returned handles, if any; and
// * marshals the returned parameters, if any, into the output buffer putting in the parameterSize field
//   if authorization sessions are present.
//
// -> This function basically consists of a switch-case-statement for each command.
TPM_RC
CommandDispatcher(
    TPMI_ST_COMMAND_TAG     tag,                                    // IN: Input command tag
    ${COMMAND}                            // IN: Command code/index
    INT32                   *parmBufferSize,                        // IN: size of parameter buffer
    BYTE                    *parmBufferStart,                       // IN: pointer to start of parameter buffer
    TPM_HANDLE              handles[],                              // IN: handle array
    UINT32                  *responseHandleSize,                    // OUT: size of handle buffer in response
    UINT32                  *respParmSize                           // OUT: size of parameter buffer in response
    )
{
    TPM_RC      rc = TPM_RC_SUCCESS;                                // the return code of the function

    // Initialization of OUT parameters
    *responseHandleSize = 0;                                        // initialize the size of the response handle buffer
    *respParmSize = 0;                                              // initialize the size of the parameter buffer

    // Get the global response buffer
    UINT8        *buffer = MemoryGetResponseBuffer(${COMMAND_VAR})
                          + sizeof(TPM_ST)                          // tag
                          + sizeof(UINT32)                          // responseSize
                          + sizeof(TPM_RC);                         // return code
    
    // Local variables
    INT32       size;                                               // size (limitation) used in marshal functions
    UINT8       *responseHandlePtr = NULL;                          // pointer to handle area
    UINT8       *respParamSizePtr = NULL;                           // pointer to size of parameter
                                                                    // used to marshal respParmSize

    if(IsHandleInResponse(${COMMAND_VAR}))                          // check for handle area in response
    {
        responseHandlePtr = buffer;
        buffer += sizeof(TPM_HANDLE);                               // adjust pointer
    }

    if(tag == TPM_ST_SESSIONS)                                      // cf. ExecCommand.c
    {
        respParamSizePtr = buffer;
        buffer += sizeof(UINT32);                                   // adjust pointer
    }

    // dispatch based on command code/index, i.e., invokes the function that performs the command actions
    switch(${SELECTOR})
    {
         ${CASES}
         default:
            pAssert(FALSE);
            break;
    }

    if(respParamSizePtr != NULL)
    {
        UINT32_Marshal(respParmSize, &respParamSizePtr, NULL);      // marshal local variable into OUT parameter
    }

    return rc;
}

#endif      //% TABLE_DRIVEN_DISPATCH                               // Spec. Version 01.19+
""")

template_outer = Template(
    """#if defined CC_${FUNC} && CC_${FUNC} == YES                  // based on Part 4
        case TPM_CC_${FUNC}:
            {
                ${IN_PARAMS}

                ${OUT_PARAMS}

                ${HANDLES}
                ${UNMARSHAL}
                if(*parmBufferSize != 0)
                    return TPM_RC_SIZE;

                ${ACTION_ROUTINE}
                ${MARSHAL}
            }
            break;
        #endif     // CC_${FUNC} == YES
        """)

template_in_params = Template(
             """// Get a buffer for input parameters (uses function from MemoryLib.c)
                ${FUNC}_In *in_params = (${FUNC}_In *) MemoryGetActionInputBuffer(sizeof(${FUNC}_In));""")

template_out_params = Template(
             """// Get a buffer for output parameters (uses function from MemoryLib.c)
                ${FUNC}_Out *out_params = (${FUNC}_Out *) MemoryGetActionOutputBuffer(sizeof(${FUNC}_Out));""")

template_unmarshal_handle = Template(
             """// Get handle ${NUM} (${PARAM}) from handles array
                in_params->${PARAM} = handles[${NUM}];
                """)

template_unmarshal = Template(
             """rc = ${TO_TYPE}_Unmarshal(&in_params->${PARAM}, &parmBufferStart, parmBufferSize${BOOL});
                if(rc != TPM_RC_SUCCESS)
                    return rc + RC_${FUNC}_${PARAM};
                """)

template_action_routine = Template(
             """// Call to the action routine for TPM2_${FUNC}
                rc = TPM2_${FUNC}(${INOUT});

                // Check the return code of action routine for TPM2_${FUNC}
                if(rc != TPM_RC_SUCCESS)
                    return rc;
                """)

template_marshal_handle = Template(
             """// Marshal handle '${PARAM}'
                *responseHandleSize += ${TO_TYPE}_Marshal(&out_params->${PARAM}, &responseHandlePtr, &size);
                """)

template_marshal = Template(
             """// Marshal parameter '${PARAM}'
                *respParmSize += ${TO_TYPE}_Marshal(&out_params->${PARAM}, &buffer, &size);
                """)
