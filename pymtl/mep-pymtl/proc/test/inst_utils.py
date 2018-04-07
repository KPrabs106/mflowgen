#=========================================================================
# inst_utils
#=========================================================================
# Includes helper functions to simplify creating assembly tests.

from pymtl import *

#-------------------------------------------------------------------------
# print_asm
#-------------------------------------------------------------------------
# Pretty print a generated assembly syntax

def print_asm( asm_code ):

  # If asm_code is a single string, then put it in a list to simplify the
  # rest of the logic.

  asm_code_list = asm_code
  if isinstance( asm_code, str ):
    asm_code_list = [ asm_code ]

  # Create a single list of lines

  asm_list = []
  for asm_seq in asm_code_list:
    asm_list.extend( asm_seq.splitlines() )

  # Print the assembly. Remove duplicate blank lines.

  prev_blank_line = False
  for asm in asm_list:
    if asm.strip() == "":
      if not prev_blank_line:
        print asm
        prev_blank_line = True
    else:
      prev_blank_line = False
      print asm

#-------------------------------------------------------------------------
# gen_nops
#-------------------------------------------------------------------------

def gen_nops( num_nops ):
  if num_nops > 0:
    return "nop\n" + ("    nop\n"*(num_nops-1))
  else:
    return ""

#-------------------------------------------------------------------------
# gen_word_data
#-------------------------------------------------------------------------

def gen_word_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".word {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_hword_data
#-------------------------------------------------------------------------

def gen_hword_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".hword {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_byte_data
#-------------------------------------------------------------------------

def gen_byte_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".byte {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_rr_src01_template
#-------------------------------------------------------------------------
# Template for register-register instructions. We first write src0
# register and then write the src1 register before executing the
# instruction under test. We parameterize the number of nops after
# writing both src registers and the instruction under test to enable
# using this template for testing various bypass paths. We also
# parameterize the register specifiers to enable using this template to
# test situations where the srce registers are equal and/or equal the
# destination register.

def gen_rr_src01_template(
  num_nops_src0, num_nops_src1, num_nops_dest,
  reg_src0, reg_src1,
  inst, src0, src1, result
):
  return """

    # Move src0 value into register
    mfc0 {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Move src1 value into register
    mfc0 {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    # Instruction under test
    {inst} r3, {reg_src0}, {reg_src1}
    {nops_dest}

    # Check the result
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rr_src10_template
#-------------------------------------------------------------------------
# Similar to the above template, except that we reverse the order in
# which we write the two src registers.

def gen_rr_src10_template(
  num_nops_src0, num_nops_src1, num_nops_dest,
  reg_src0, reg_src1,
  inst, src0, src1, result
):
  return """

    # Move src1 value into register
    mfc0 {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    # Move src0 value into register
    mfc0 {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Instruction under test
    {inst} r3, {reg_src0}, {reg_src1}
    {nops_dest}

    # Check the result
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rr_dest_byp_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a mfc0 instruction.

def gen_rr_dest_byp_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 8, num_nops, "r1", "r2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src1_byp_test
#-------------------------------------------------------------------------
# Test the source 1 bypass paths by varying how many nops are inserted
# between writing the src1 register and reading this register in the
# instruction under test.

def gen_rr_src1_byp_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 8-num_nops, num_nops, 0, "r1", "r2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_byp_test
#-------------------------------------------------------------------------
# Test the source 0 bypass paths by varying how many nops are inserted
# between writing the src0 register and reading this register in the
# instruction under test.

def gen_rr_src0_byp_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src10_template( num_nops, 8-num_nops, 0, "r1", "r2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_srcs_byp_test
#-------------------------------------------------------------------------
# Test both source bypass paths at the same time by varying how many nops
# are inserted between writing both src registers and reading both
# registers in the instruction under test.

def gen_rr_srcs_byp_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 0, num_nops, 0, "r1", "r2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src0 register specifier is the same as the
# destination register specifier.

def gen_rr_src0_eq_dest_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "r3", "r2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src1_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src1 register specifier is the same as the
# destination register specifier.

def gen_rr_src1_eq_dest_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "r1", "r3",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_eq_src1_test
#-------------------------------------------------------------------------
# Test situation where the src register specifiers are the same.

def gen_rr_src0_eq_src1_test( inst, src, result ):
  return gen_rr_src01_template( 0, 0, 0, "r1", "r1",
                                inst, src, src, result )

#-------------------------------------------------------------------------
# gen_rr_srcs_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where all three register specifiers are the same.

def gen_rr_srcs_eq_dest_test( inst, src, result ):
  return gen_rr_src01_template( 0, 0, 0, "r3", "r3",
                                inst, src, src, result )

#-------------------------------------------------------------------------
# gen_rr_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-register instruction under
# test. We assume that bypassing has already been tested.

def gen_rr_value_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "r1", "r2",
                                inst, src0, src1, result )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

#-------------------------------------------------------------------------
# gen_rimm_template
#-------------------------------------------------------------------------
# Template for register-immediate instructions. We first write the src
# register before executing the instruction under test. We parameterize
# the number of nops after writing the src register and the instruction
# under test to enable using this template for testing various bypass
# paths. We also parameterize the register specifiers to enable using
# this template to test situations where the srce registers are equal
# and/or equal the destination register.

def gen_rimm_template(
  num_nops_src, num_nops_dest,
  reg_src,
  inst, src, imm, result
):
  return """

    # Move src value into register
    mfc0 {reg_src}, mngr2proc < {src}
    {nops_src}

    # Instruction under test
    {inst} r3, {reg_src}, {imm}
    {nops_dest}

    # Check the result
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_src  = gen_nops(num_nops_src),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rimm_dest_byp_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a mfc0 instruction.

def gen_rimm_dest_byp_test( num_nops, inst, src, imm, result ):
  return gen_rimm_template( 8, num_nops, "r1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_src_byp_test
#-------------------------------------------------------------------------
# Test the source bypass paths by varying how many nops are inserted
# between writing the src register and reading this register in the
# instruction under test.

def gen_rimm_src_byp_test( num_nops, inst, src, imm, result ):
  return gen_rimm_template( num_nops, 0, "r1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_src_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src register specifier is the same as the
# destination register specifier.

def gen_rimm_src_eq_dest_test( inst, src, imm, result ):
  return gen_rimm_template( 0, 0, "r3",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-immediate instruction under
# test. We assume that bypassing has already been tested.

def gen_rimm_value_test( inst, src, imm, result ):
  return gen_rimm_template( 0, 0, "r1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_imm_template
#-------------------------------------------------------------------------
# Template for immediate instructions. We parameterize the number of nops
# after the instruction under test to enable using this template for
# testing various bypass paths.

def gen_imm_template( num_nops_dest, inst, imm, result ):
  return """

    # Instruction under test
    {inst} r3, {imm}
    {nops_dest}

    # Check the result
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_imm_dest_byp_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a mfc0 instruction.

def gen_imm_dest_byp_test( num_nops, inst, imm, result ):
  return gen_imm_template( num_nops, inst, imm, result )

#-------------------------------------------------------------------------
# gen_imm_value_test
#-------------------------------------------------------------------------
# Test the actual operation of an immediate instruction under test. We
# assume that bypassing has already been tested.

def gen_imm_value_test( inst, imm, result ):
  return gen_imm_template( 0, inst, imm, result )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

#-------------------------------------------------------------------------
# gen_br2_template
#-------------------------------------------------------------------------
# Template for branch instructions with two sources. We test two forward
# branches and one backwards branch. The way we actually do the test is
# we update a register to reflect the control flow; certain bits in this
# register are set at different points in the program. Then we can check
# the control flow bits at the end to see if only the bits we expect are
# set (i.e., the program only executed those points that we expect). Note
# that test also makes sure that the instruction in the branch delay slot
# is _not_ executed.

# We currently need the id to create labels unique to this test. We might
# eventually allow local labels (e.g., 1f, 1b) as in gas.

gen_br2_template_id = 0

def gen_br2_template(
  num_nops_src0, num_nops_src1,
  reg_src0, reg_src1,
  inst, src0, src1, taken
):

  # Determine the expected control flow pattern

  if taken:
    control_flow_pattern = 0b101010
  else:
    control_flow_pattern = 0b111111

  # Create unique labels

  global gen_br2_template_id
  id_a = "label_{}".format( gen_br2_template_id + 1 )
  id_b = "label_{}".format( gen_br2_template_id + 2 )
  id_c = "label_{}".format( gen_br2_template_id + 3 )
  gen_br2_template_id += 3

  return """

    # r3 will track the control flow pattern
    addiu  r3, r0, 0

    # Move src0 value into register
    mfc0   {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Move src1 value into register
    mfc0   {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    {inst} {reg_src0}, {reg_src1}, {id_a}  # br -.
    addiu  r3, r3, 0b000001                #     |
                                           #     |
{id_b}:                                    # <---+-.
    addiu  r3, r3, 0b000010                #     | |
                                           #     | |
    {inst} {reg_src0}, {reg_src1}, {id_c}  # br -+-+-.
    addiu  r3, r3, 0b000100                #     | | |
                                           #     | | |
{id_a}:                                    # <---' | |
    addiu  r3, r3, 0b001000                #       | |
                                           #       | |
    {inst} {reg_src0}, {reg_src1}, {id_b}  # br ---' |
    addiu  r3, r3, 0b010000                #         |
                                           #         |
{id_c}:                                    # <-------'
    addiu  r3, r3, 0b100000                #

    # Check the control flow pattern
    mtc0   r3, proc2mngr > {control_flow_pattern}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_br2_src1_byp_test
#-------------------------------------------------------------------------
# Test the source 1 bypass paths by varying how many nops are inserted
# between writing the src1 register and reading this register in the
# instruction under test.

def gen_br2_src1_byp_test( num_nops, inst, src0, src1, taken ):
  return gen_br2_template( 8-num_nops, num_nops, "r1", "r2",
                           inst, src0, src1, taken )

#-------------------------------------------------------------------------
# gen_br2_src0_byp_test
#-------------------------------------------------------------------------
# Test the source 0 bypass paths by varying how many nops are inserted
# between writing the src0 register and reading this register in the
# instruction under test.

def gen_br2_src0_byp_test( num_nops, inst, src0, src1, result ):
  return gen_br2_template( num_nops, 0, "r1", "r2",
                           inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_br2_srcs_byp_test
#-------------------------------------------------------------------------
# Test both source bypass paths at the same time by varying how many nops
# are inserted between writing both src registers and reading both
# registers in the instruction under test.

def gen_br2_srcs_byp_test( num_nops, inst, src0, src1, result ):
  return gen_br2_template( 0, num_nops, "r1", "r2",
                           inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_br2_src0_eq_src1_test
#-------------------------------------------------------------------------
# Test situation where the src register specifiers are the same.

def gen_br2_src0_eq_src1_test( inst, src, result ):
  return gen_br2_template( 0, 0, "r1", "r1",
                                 inst, src, src, result )

#-------------------------------------------------------------------------
# gen_br2_value_test
#-------------------------------------------------------------------------
# Test the correct branch resolution based on various source values.

def gen_br2_value_test( inst, src0, src1, taken ):
  return gen_br2_template( 0, 0, "r1", "r2", inst, src0, src1, taken )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

#-------------------------------------------------------------------------
# gen_br1_template
#-------------------------------------------------------------------------
# Template for branch instructions with one source. We test two forward
# branches and one backwards branch. The way we actually do the test is
# we update a register to reflect the control flow; certain bits in this
# register are set at different points in the program. Then we can check
# the control flow bits at the end to see if only the bits we expect are
# set (i.e., the program only executed those points that we expect). Note
# that test also makes sure that the instruction in the branch delay slot
# is _not_ executed.

# We currently need the id to create labels unique to this test. We might
# eventually allow local labels (e.g., 1f, 1b) as in gas.

gen_br1_template_id = 0

def gen_br1_template( num_nops_src, reg_src, inst, src, taken ):

  # Determine the expected control flow pattern

  if taken:
    control_flow_pattern = 0b101010
  else:
    control_flow_pattern = 0b111111

  # Create unique labels

  global gen_br1_template_id
  id_a = "label_{}".format( gen_br1_template_id + 1 )
  id_b = "label_{}".format( gen_br1_template_id + 2 )
  id_c = "label_{}".format( gen_br1_template_id + 3 )
  gen_br1_template_id += 3

  return """

    # r3 will track which branches were taken
    addiu  r3, r0, 0

    # Move src value into register
    mfc0   {reg_src}, mngr2proc < {src}
    {nops_src}

    {inst} {reg_src}, {id_a}  # br -.
    addiu  r3, r3, 0b000001   #     |
                              #     |
{id_b}:                       # <---+-.
    addiu  r3, r3, 0b000010   #     | |
                              #     | |
    {inst} {reg_src}, {id_c}  # br -+-+-.
    addiu  r3, r3, 0b000100   #     | | |
                              #     | | |
{id_a}:                       # <---' | |
    addiu  r3, r3, 0b001000   #       | |
                              #       | |
    {inst} {reg_src}, {id_b}  # br ---' |
    addiu  r3, r3, 0b010000   #         |
                              #         |
{id_c}:                       # <-------'
    addiu  r3, r3, 0b100000   #

    # Check the control flow pattern
    mtc0 r3, proc2mngr > {control_flow_pattern}

  """.format(
    nops_src = gen_nops(num_nops_src),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_br1_src_byp_test
#-------------------------------------------------------------------------
# Test the source bypass paths by varying how many nops are inserted
# between writing the src register and reading this register in the
# instruction under test.

def gen_br1_src_byp_test( num_nops, inst, src, taken ):
  return gen_br1_template( num_nops, "r1", inst, src, taken )

#-------------------------------------------------------------------------
# gen_br1_value_test
#-------------------------------------------------------------------------
# Test the correct branch resolution based on various source values.

def gen_br1_value_test( inst, src, taken ):
  return gen_br1_template( 0, "r1", inst, src, taken )

#-------------------------------------------------------------------------
# gen_jal_link_byp_test
#-------------------------------------------------------------------------
# Currently we have to hard code the expected link address. Not sure if
# there is a cleaner way to do this.

# We currently need the id to create labels unique to this test. We might
# eventually allow local labels (e.g., 1f, 1b) as in gas.

gen_jal_link_byp_id = 0

def gen_jal_link_byp_test( num_nops, link_addr ):

  global gen_jal_link_byp_id

  # Create unique labels

  id_a = "label_{}".format( gen_jal_link_byp_id + 1 )
  gen_jal_link_byp_id += 1

  return """

    # Use r3 to track the control flow pattern
    addiu r3, r0, 0

    jal   {id_a}
    addiu r3, r3, 0b01

{id_a}:
    {nops}
    mtc0  r31, proc2mngr > {link_addr}
    addiu r3, r3, 0b10

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b10

  """.format(
    nops = gen_nops(num_nops),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_jr_src_byp_test
#-------------------------------------------------------------------------
# Test the source bypass paths by varying how many nops are inserted
# between writing the src register and reading this register in the
# instruction under test.

# We currently need the id to create labels unique to this test. We might
# eventually allow local labels (e.g., 1f, 1b) as in gas.

gen_jr_src_byp_id = 0

def gen_jr_src_byp_test( num_nops ):

  # Create unique labels

  global gen_jr_src_byp_id
  id_a = "label_{}".format( gen_jr_src_byp_id + 1 )
  gen_jr_src_byp_id += 1

  return """

    # Use r3 to track the control flow pattern
    addiu r3, r0, 0

    # Move src value into register
    lui   r1,     %hi[{id_a}]
    ori   r1, r0, %lo[{id_a}]
    {nops}

    jr    r1

    addiu r3, r3, 0b01

{id_a}:
    addiu r3, r3, 0b10

    # Only the second bit should be set if jump was taken
    mtc0  r3, proc2mngr > 0b10

  """.format(
    nops = gen_nops(num_nops),
    **locals()
  )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

#-------------------------------------------------------------------------
# gen_ld_template
#-------------------------------------------------------------------------
# Template for load instructions. We first write the base register before
# executing the instruction under test. We parameterize the number of
# nops after writing the base register and the instruction under test to
# enable using this template for testing various bypass paths. We also
# parameterize the register specifiers to enable using this template to
# test situations where the base register is equal to the destination
# register.

def gen_ld_template(
  num_nops_base, num_nops_dest,
  reg_base,
  inst, offset, base, result
):
  return """

    # Move base value into register
    mfc0 {reg_base}, mngr2proc < {base}
    {nops_base}

    # Instruction under test
    {inst} r3, {offset}({reg_base})
    {nops_dest}

    # Check the result
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_base = gen_nops(num_nops_base),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_ld_dest_byp_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a mfc0 instruction.

def gen_ld_dest_byp_test( num_nops, inst, base, result ):
  return gen_ld_template( 8, num_nops, "r1", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_base_byp_test
#-------------------------------------------------------------------------
# Test the base register bypass paths by varying how many nops are
# inserted between writing the base register and reading this register in
# the instruction under test.

def gen_ld_base_byp_test( num_nops, inst, base, result ):
  return gen_ld_template( num_nops, 0, "r1", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_base_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the base register specifier is the same as the
# destination register specifier.

def gen_ld_base_eq_dest_test( inst, base, result ):
  return gen_ld_template( 0, 0, "r3", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-register instruction under
# test. We assume that bypassing has already been tested.

def gen_ld_value_test( inst, offset, base, result ):
  return gen_ld_template( 0, 0, "r1", inst, offset, base, result )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

#-------------------------------------------------------------------------
# gen_st_template
#-------------------------------------------------------------------------
# Template for store instructions. We first write the src and base
# registers before executing the instruction under test. We parameterize
# the number of nops after writing these register and the instruction
# under test to enable using this template for testing various bypass
# paths. We also parameterize the register specifiers to enable using
# this template to test situations where the base register is equal to
# the destination register. We use a lw to bring back in the stored data
# to verify the store. The lw address is formed by simply masking off the
# lower two bits of the store address. The result needs to be specified
# accordingly. This helps make sure that the store doesn't store more
# data then it is supposed to.

def gen_st_template(
  num_nops_src, num_nops_base, num_nops_dest,
  reg_src, reg_base,
  inst, src, offset, base, result
):
  return """

    # Move src value into register
    mfc0 {reg_src}, mngr2proc < {src}
    {nops_src}

    # Move base value into register
    mfc0 {reg_base}, mngr2proc < {base}
    {nops_base}

    # Instruction under test
    {inst} {reg_src}, {offset}({reg_base})
    {nops_dest}

    # Check the result
    mfc0 r4, mngr2proc < {lw_base}
    lw   r3, 0(r4)
    mtc0 r3, proc2mngr > {result}

  """.format(
    nops_src  = gen_nops(num_nops_src),
    nops_base = gen_nops(num_nops_base),
    nops_dest = gen_nops(num_nops_dest),
    lw_base   = (base + offset) & 0xfffffffc,
    **locals()
  )

#-------------------------------------------------------------------------
# gen_st_dest_byp_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a lw instruction.

def gen_st_dest_byp_test( num_nops, inst, src, base, result ):
  return gen_st_template( 0, 8, num_nops, "r1", "r2",
                          inst, src, 0, base, result )

#-------------------------------------------------------------------------
# gen_st_base_byp_test
#-------------------------------------------------------------------------
# Test the base register bypass paths by varying how many nops are
# inserted between writing the base register and reading this register in
# the instruction under test.

def gen_st_base_byp_test( num_nops, inst, src, base, result ):
  return gen_st_template( 8-num_nops, num_nops, 0, "r1", "r2",
                          inst, src, 0, base, result )

#-------------------------------------------------------------------------
# gen_st_src_byp_test
#-------------------------------------------------------------------------
# Test the src register bypass paths by varying how many nops are
# inserted between writing the src register and reading this register in
# the instruction under test.

def gen_st_src_byp_test( num_nops, inst, src, base, result ):
  return gen_st_template( num_nops, 0, 0, "r1", "r2",
                          inst, src, 0, base, result )

#-------------------------------------------------------------------------
# gen_st_srcs_byp_test
#-------------------------------------------------------------------------
# Test both source bypass paths at the same time by varying how many nops
# are inserted between writing both src registers and reading both
# registers in the instruction under test.

def gen_st_srcs_byp_test( num_nops, inst, src, base, result ):
  return gen_st_template( 0, num_nops, 0, "r1", "r2",
                          inst, src, 0, base, result )

#-------------------------------------------------------------------------
# gen_st_src_eq_base_test
#-------------------------------------------------------------------------
# Test situation where the src register specifier is the same as the base
# register specifier.

def gen_st_src_eq_base_test( inst, src, result ):
  return gen_st_template( 0, 0, 0, "r1", "r1",
                          inst, src, 0, src, result )

#-------------------------------------------------------------------------
# gen_st_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a store instruction under test. We assume
# that bypassing has already been tested.

def gen_st_value_test( inst, src, offset, base, result ):
  return gen_st_template( 0, 0, 0, "r1", "r2",
                          inst, src, offset, base, result )

#-------------------------------------------------------------------------
# gen_st_random_test
#-------------------------------------------------------------------------
# Similar to gen_st_value_test except that we can specifically use lhu or
# lbu so that we don't need to worry about the high order bits.

def gen_st_random_test( inst, ld_inst, src, offset, base ):
  return """

    # Move src value into register
    mfc0 r1, mngr2proc < {src}

    # Move base value into register
    mfc0 r2, mngr2proc < {base}

    # Instruction under test
    {inst} r1, {offset}(r2)

    # Check the result
    mfc0 r4, mngr2proc < {ld_base}
    {ld_inst} r3, 0(r4)
    mtc0 r3, proc2mngr > {src}

  """.format(
    ld_base = (base + offset),
    **locals()
  )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

#=========================================================================
# TestHarness
#=========================================================================

class TestHarness (Model):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, ProcModel, src_delay, sink_delay,
                              mem_stall_prob, mem_latency ):

    s.src    = TestSource    ( 32, [], src_delay  )
    s.sink   = TestSink      ( 32, [], sink_delay )
    s.proc   = ProcModel     ()
    s.mem    = TestMemory    ( MemMsg4B(), 2, mem_stall_prob, mem_latency )

    # Processor <-> Proc/Mngr

    s.connect( s.proc.mngr2proc, s.src.out         )
    s.connect( s.proc.proc2mngr, s.sink.in_        )

    # Processor <-> Memory

    s.connect( s.proc.imemreq,   s.mem.reqs[0]     )
    s.connect( s.proc.imemresp,  s.mem.resps[0]    )
    s.connect( s.proc.dmemreq,   s.mem.reqs[1]     )
    s.connect( s.proc.dmemresp,  s.mem.resps[1]    )

  #-----------------------------------------------------------------------
  # load
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc src

      if section.name == ".mngr2proc":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.src.src.msgs.append( Bits(32,bits) )

      # For .proc2mngr sections, copy section into proc2mngr_ref src

      elif section.name == ".proc2mngr":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.sink.sink.msgs.append( Bits(32,bits) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # cleanup
  #-----------------------------------------------------------------------

  def cleanup( s ):
    del s.mem.mem[:]

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.src.done and s.sink.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.proc.line_trace() + "|" + \
           s.mem.line_trace()  + " > " + \
           s.sink.line_trace()

#=========================================================================
# run_test
#=========================================================================

def run_test( ProcModel, gen_test, src_delay=0, sink_delay=0,
                                   mem_stall_prob=0, mem_latency=0,
                                   max_cycles=5000 ):

  # Instantiate and elaborate the model

  model = TestHarness( ProcModel, src_delay, sink_delay,
                                  mem_stall_prob, mem_latency  )
  model.elaborate()

  # Assemble the test program

  mem_image = assemble( gen_test() )

  # Load the program into the model

  model.load( mem_image )

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done() and sim.ncycles < max_cycles:
    sim.print_line_trace()
    sim.cycle()

  # Force a test failure if we timed out

  assert sim.ncycles < max_cycles

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  model.cleanup()
