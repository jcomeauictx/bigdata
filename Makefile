# Makefile for simple approach without frameworks
SHELL := /bin/bash
TRUNCATE ?= 9
PYTHON ?= python
INPUT ?= /tmp/example
export

env:
	env

all: first second third
first: $(INPUT)/combined.csv
second: $(INPUT)/calculated.csv
third: $(INPUT)/joined.csv

$(INPUT):
	[ -d $@ ] || mkdir -p $@

$(INPUT)/data: data $(INPUT)
	[ -d $@ ] || cp -a $< $(dir $@)

$(INPUT)/combined.csv: $(INPUT)/data
	cat $</{billing,salesmen}.csv | $(PYTHON) ./removeheaders.py > $@
	
$(INPUT)/calculated.csv: $(INPUT)/data/sales.csv
	cat $< | $(PYTHON) ./calculate.py net gross -expenses > $@

$(INPUT)/joined.csv: $(INPUT)/combined.csv $(INPUT)/calculated.csv
	cat $(word 1, $+) | $(PYTHON) ./left_outer_join.py id $(word 2, $+) > $@

/tmp/example:
	mkdir -p $@
%.pylint: %.py
	pylint $<
%.doctest: %.py
	python -m doctest $<
doctest: *.py
	for file in $$(grep -l '>>>' $+); do \
	 $(MAKE) $${file%%.py}.doctest; \
	done
clean:
	[ "$(dir $(INPUT))" = "/tmp/" ] && rm -rf $(INPUT)
