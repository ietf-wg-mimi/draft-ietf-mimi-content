edn  := $(wildcard *.edn)
cbor := $(patsubst %.edn,%.cbor,$(wildcard *.edn))
pretty := $(patsubst %.edn,%.pretty,$(wildcard *.edn))
targets := $(cbor) $(pretty)
current_dir := $(shell pwd)
.SECONDARY: $(%.diag)
#cbortemp    := $(patsubst %.edn,%.cbor.tmp,$(wildcard *.edn))
cborcontent := $(filter-out implied-original.cbor,$(cbor))
edncontent  := $(filter-out implied-original.edn ,$(edn))

# fix multiline concatenated strings before converting from EDN to CBOR:
#   gsed -z -r -e "s/' [+]\n +'//g"

all: $(targets)

#%.diag: %.edn
#	edn-abnf -t diag $< > $@

#%.cbor: %.diag
#	diag2cbor.rb $< > $@

%.pretty: %.cbor
	cbor2pretty.rb $< > $@

#%.cbor.tmp: %.edn
#	edn2cbor $< $@
#	cmp $@ `basename $@ .tmp`
#        rm $@

validate-all: validate-content validate-edn validate-implied

validate-content: $(cborcontent)
	cddl-rs compile-cddl --cddl ../mimi-content.cddl
	for c in $(cborcontent); do cddl ../mimi-content.cddl validate $${c}; done

validate-edn: $(edncontent)
	for c in $(edncontent); do ./compare_edn_to_cbor.sh $${c}; done

# application/mimi-message-status has moved to another document
#validate-report: report.cbor
#	cddl-rs compile-cddl --cddl ../delivery-report.cddl
#	cddl ../delivery-report.cddl validate report.cbor
#	#cddl-rs validate -d ../delivery-report.cddl -c report.cbor

validate-implied: implied-original.cbor
	cddl-rs compile-cddl --cddl ../implied.cddl
	cddl ../implied.cddl validate implied-original.cbor
	#cddl-rs validate -d ../implied.cddl -c implied-original.cbor

help:
	@echo '1. Install these things:'
	@echo '  (sudo) gem install cbor-diag'
	@echo '  (sudo) gem install edn-abnf'
	@echo '  (sudo) gem install cddl'
	@echo '  cargo install cddl'
	@echo '2. Then fix your paths (especially on a Mac)'
	@echo '3. Profit'

.SUFFIXES:
