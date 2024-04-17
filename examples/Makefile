targets := $(patsubst %.edn,%.cbor,$(wildcard *.edn)) $(patsubst %.edn,%.pretty,$(wildcard *.edn))
current_dir := $(shell pwd)
.SECONDARY: $(%.diag)

all: $(targets)

%.diag: %.edn
	edn2diag $< $@

%.cbor: %.diag
	diag2cbor.rb $< > $@

%.pretty: %.diag
	diag2pretty.rb $< > $@

.SUFFIXES:


