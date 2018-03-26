#=========================================================================
# configure.mk
#=========================================================================
# This file will be included inside the Makefile in the build directory

#-------------------------------------------------------------------------
# ASCII art
#-------------------------------------------------------------------------

define ascii.innovus-init
	@echo -e $(echo_green)
	@echo '#################################################################################'
	@echo '#                           _____ _   _ _____ _______                           #'
	@echo '#                          |_   _| \ | |_   _|__   __|                          #'
	@echo '#                            | | |  \| | | |    | |                             #'
	@echo '#                            | | | . ` | | |    | |                             #'
	@echo '#                           _| |_| |\  |_| |_   | |                             #'
	@echo '#                          |_____|_| \_|_____|  |_|                             #'
	@echo '#                                                                               #'
	@echo '#################################################################################'
	@echo -e $(echo_nocolor)
endef

#-------------------------------------------------------------------------
# Alias -- short name for this step
#-------------------------------------------------------------------------

init: innovus-init

#-------------------------------------------------------------------------
# Variables shared across all Innovus steps
#-------------------------------------------------------------------------
# The Innovus execute commands should be set up during Innovus flow setup
#
# - $(innovus_exec)
# - $(innovus_exec_gui)
#
# The Innovus directories should also be set up during Innovus flow setup
#
# - $(innovus_logs_dir)
# - $(innovus_results_dir)
# - $(innovus_reports_dir)
# - $(innovus_handoffs_dir)

#-------------------------------------------------------------------------
# Primary command target
#-------------------------------------------------------------------------
# These are the commands run when executing this step. These commands are
# included into the build Makefile.

define commands.innovus-init
	$(innovus_exec) -init $(innovus_flowsetup_handoffs_dir)/INNOVUS/run_init.tcl -log $(innovus_logs_dir)/init.log
endef

#-------------------------------------------------------------------------
# Extra targets
#-------------------------------------------------------------------------
# These are extra useful targets when working with this step. These
# targets are included into the build Makefile.

debug-innovus-init:
	export STEP=init && $(innovus_exec_gui) -init $(innovus_flowsetup_handoffs_dir)/INNOVUS/run_debug.tcl -log $(innovus_logs_dir)/debug.log

clean-innovus-init:
	rm -rf ./$(VPATH)/innovus-init
	rm -rf ./$(innovus_logs_dir)/init.*
	rm -rf ./$(innovus_reports_dir)/init.*
	rm -rf ./$(innovus_handoffs_dir)/init.*

debug-init: debug-innovus-init
clean-init: clean-innovus-init

