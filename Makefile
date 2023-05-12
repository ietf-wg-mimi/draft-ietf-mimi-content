draft = $(shell basename *.md .md)
targets = $(draft).html $(draft).txt
version = $(shell sed -nr 's/value = \"[a-z-]*([0-9][0-9])\"/\1/p' *.md)

all: $(targets)

%.xml: %.md
	mmark $< > $@

%.html: %.xml
	xml2rfc --html --v3 $<

%.txt: %.xml
	xml2rfc --text --v3 $<

idnits: $(draft).txt
	idnits $<

submit: $(draft).xml
	cp $(draft).xml submitted/$(draft)-$(version).xml 

