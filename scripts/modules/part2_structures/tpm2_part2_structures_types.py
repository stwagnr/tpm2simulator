# -*- coding: utf-8 -*-

from textwrap import dedent


# Class containing header and footer for "BaseTypes.h" file
class BaseTypes:

    def __init__(self):
        return

    '''
    The following code is based on Part 4 (Section 'Header Files -> BaseTypes.h')
    '''
    BASETYPE_HEADER = dedent("""\
                                    #ifndef _BASETYPES_H
                                    #define _BASETYPES_H

                                    #include "stdint.h"

                                    // NULL definition
                                    #ifndef               NULL
                                    #define               NULL            (0)
                                    #endif

                                    """)

    '''
    The following code is based on Part 4 (Section 'Header Files -> BaseTypes.h')
    '''
    BASETYPE_FOOTER = dedent("""\
                                    typedef struct {
                                        UINT16        size;
                                        BYTE          buffer[1];
                                    } TPM2B;

                                    #endif
                                    """)


# Class containing header and footer for "TPM_Types.h" file
class TpmTypes:

    def __init__(self):
        return

    '''
    The following code is a simple #ifndef for a header file with a three necessary includes
    '''
    TPMTYPES_HEADER = dedent("""\
                                    #ifndef _TPM_TYPES_H_
                                    #define _TPM_TYPES_H_

                                    #include    "BaseTypes.h"       // i.a. needed for UINT32
                                    #include    "Implementation.h"  // i.a. needed for TPM_ALG_ID
                                    #include    "Capabilities.h"    // i.a. needed for MAX_CAP_CC

                                    """)

    '''
    The following code is the corresponding #endif for the previous #ifndef
    '''
    TPMTYPES_FOOTER = dedent("""\
                                    #endif    //  _TPM_TYPES_H_
                                    """)
