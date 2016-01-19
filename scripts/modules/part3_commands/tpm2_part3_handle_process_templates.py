# -*- coding: utf-8 -*-

from string import Template
from textwrap import dedent

# This file contains templates used to generate HandleProcess file

'''
The following template is based on Part 4 (Section ParseHandleBuffer())
'''
handle_process_template = Template(dedent("""\
    #include    "Tpm.h"
    #include    "InternalRoutines.h"
    #include    "HandleProcess_fp.h"
    ${TABLE_DRIVEN_DISPATCH_IFNDEF}
    TPM_RC
    ParseHandleBuffer(
        ${COMMAND}          // IN: Command being processed
        BYTE            **handleBufferStart,    // IN/OUT: command buffer where handles
                                                //     are located. Updated as handles
                                                //     are unmarshaled
        INT32           *bufferRemainingSize,   // IN/OUT: indicates the amount of data
                                                //     left in the command buffer.
                                                //     Updated as handles are
                                                //     unmarshaled
        TPM_HANDLE       handles[],             // OUT: Array that receives the handles
        UINT32          *handleCount            // OUT: Receives the count of handles
        )
    {
        TPM_RC      result;                     // The result (from the function definition)

        switch(${SELECTOR}) {                   // based on Part 3 (command tables).
            ${CASES}
            default:
                    pAssert(FALSE);
                    break;
    }
            return TPM_RC_SUCCESS;
    }

    ${TABLE_DRIVEN_DISPATCH_ENDIF}
        """))

"""
Template variables: FUNC, NUM_HANDLES, EXTENSION

The following template is based on Part 4 (Section ParseHandleBuffer())
"#if defined" is based on Part 4, Annex A, Implementation.h
"""
handle_process_template_outer = Template("""
#if defined CC_${FUNC} && CC_${FUNC} == YES
        case TPM_CC_${FUNC}:
            *handleCount = ${NUM_HANDLES}; ${EXTENSION}
            break;
#endif     // CC_${FUNC}
""")

"""
Template variables: HANDLE, BOOL, NUM

The following template is based on Part 4 (Section ParseHandleBuffer())
"""
handle_process_template_inner = Template("""\
        result = ${HANDLE}_Unmarshal(&handles[${NUM}],  handleBufferStart, bufferRemainingSize${BOOL});
        if(result != TPM_RC_SUCCESS)
            return result + TPM_RC_H + TPM_RC_${NUM2};\
""")