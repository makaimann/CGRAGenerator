################################################################################
# Makefile Definitions
################################################################################

VERILATOR_TOP := ../verilator/generator_z_tb
HARDWARE_TOP  :=  ../hardware/generator_z/top

SILENT := FALSE
ifeq ($(SILENT), TRUE)
	QUIET := -q
	VSWITCH :=
else
	QUIET :=
	VSWITCH := -v
endif
# $(warning OUTPUT = "$(OUTPUT)")

TEMPDIR := $(shell mktemp -d /tmp/gentest-XXX)
DELAY = 0,0

pw_gray_small_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small" \
	CONFIG="-config ../../bitstream/examples/pw1009.bsa"

pw_gray_8x8:
	make test TEMPDIR=$(TEMPDIR) IMAGE="gray" \
	CONFIG="-config ../../bitstream/examples/pwv2.bs"

test_basic:
#	# Use run.csh built-in default config
	@./writelog.csh log1 -init
#	# make test TEMPDIR=$(TEMPDIR) IMAGE="gray_small"         DELAY="0,0"
	make test TEMPDIR=$(TEMPDIR) IMAGE="input_10x10_1to100" DELAY="0,0" \
	          CONFIG=""
	@echo
	@./writelog.csh log1 -print

update_cgra:
	cd $(HARDWARE_TOP); ./run.csh

test_unit:
#	Doesn't work anyway, may as well comment it out (for now at least)
#	make update_cgra
	./unit_tests/utest $(VSWITCH)



test_all:
	make hackdiff_test 2>&1 | tee $(TEMPDIR)/hackdiff_test.log
	make test_unit
	make test_basic
	make test_serpent

        # Read standalone test result(s) from 'log1'
	@echo ""
	@echo SUMMARY OF STANDALONE TEST RESULTS
	@echo ==================================================
	./writelog.csh log1 -print

        # Summary of hackdiff results
	egrep ^hackdiff $(TEMPDIR)/hackdiff_test.log


test_serpent_dev:
	../bitstream/bsbuilder/testdir/make_bitstreams.csh $(TEMPDIR) pointwise conv_1_2 conv_2_1
	../bitstream/bsbuilder/testdir/test_bitstreams.csh $(TEMPDIR) pointwise conv_1_2 conv_2_1
	../bitstream/bsbuilder/testdir/make_bitstreams.csh $(TEMPDIR) conv_3_1
	../bitstream/bsbuilder/testdir/test_bitstreams.csh $(TEMPDIR) conv_3_1
	../bitstream/bsbuilder/testdir/make_bitstreams.csh $(TEMPDIR) conv_bw
	../bitstream/bsbuilder/testdir/test_bitstreams.csh $(TEMPDIR) conv_bw

test_serpent:
	../bitstream/bsbuilder/testdir/make_bitstreams.csh $(TEMPDIR)
	../bitstream/bsbuilder/testdir/test_bitstreams.csh $(TEMPDIR)
#	FIXME Who will delete TEMPDIR?

test_standalone:
# 	pwd; ls
	./writelog.csh log1 -init TEST SUMMARY BEGIN `date`

        # Note: Results go to 'log1'
	make pw_gray_small_8x8
#	make pw_gray_8x8
# 	# make gray_small_4x4
# 	# make gray_4x4

# Probably want to restore the more-challenging conv_bw test, once smoke has cleared.
# hackdiff_test:
# 	cd ../bitstream; \
# 	decoder/hackdiff.csh \
# 	  examples/conv_bw.bs examples/conv_bw.bsa \
# 	  -cgra examples/cgra_configs/cgra_info_8x8.txt

hackdiff_test:
	cd ../bitstream; \
	decoder/hackdiff.csh \
	  examples/bw1000.bs examples/bw1000.bsa \
	  -cgra examples/cgra_configs/cgra_info_new.txt



# TODO can combine all these down to one
# TODO make it look more like other makefile (cgraflow)


test:
	@echo ""
	@echo "------------------------------------------------------------------------"
	@echo "BEGIN TEST"
	@echo "------------------------------------------------------------------------"

	cd $(VERILATOR_TOP);\
	./run.csh $(QUIET) -gen top_tb.cpp  \
	   $(CONFIG)                         \
	   -input  io/$(IMAGE).png            \
	   -output $(TEMPDIR)/$(IMAGE)_out.raw \
	   -delay $(DELAY) \
	   -nclocks 5M || echo FAIL

	cmp $(VERILATOR_TOP)/io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw      \
		&& ./writelog.csh log1 PASSED `date +%R` test $(IMAGE) \
		|| ./writelog.csh log1 FAILED `date +%R` test $(IMAGE)

	cd $(VERILATOR_TOP);\
	cmp io/$(IMAGE)_out.raw $(TEMPDIR)/$(IMAGE)_out.raw

