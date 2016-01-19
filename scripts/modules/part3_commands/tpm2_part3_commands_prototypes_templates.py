# -*- coding: utf-8 -*-

from string import Template

# This file contains templates used in generating command prototypes

command_prototype_template = Template("""\
${COMMAND_IFDEF}
#ifndef ${NAME}
#define ${NAME}

// Type definition for input structure
${STRUCTURE_IN}

// Type definition for output structure
${STRUCTURE_OUT}

// Definition of response code modifiers
${MODIFIERS}

// Declaration of function prototypes
${FUNCTIONS}

#endif // ${NAME}
${COMMAND_ENDIF}
""")

command_ifdef = Template("""#ifdef TPM_CC_${NAME} // Command must be defined\n""")

command_endif = Template("""#endif  // TPM_CC_${NAME}\n""")

structure_member = Template("""\t${OLD_TYPE}\t\t${NEW_TYPE};\n""")

structure_in = Template("""\
typedef struct {
${MEMBERS}
} ${NAME}_In;""")

structure_out = Template("""\
typedef struct {
${MEMBERS}
} ${NAME}_Out;""")
