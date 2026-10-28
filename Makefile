# Get BOBILib's files into data/ for the code and scripts of this repository.
#
#   make fetch-data    build data/: copy instances/, download the rest from BOBILib's GitLab,
#                      check every file against data-manifest/bobilib_snapshot.tsv
#   make verify-data   only check the files already in data/
#
# Options (see scripts/fetch_data.py --help):
#   SUBSET=used        used (default): the 1,503 instances with a certificate or solution file
#                      in results/, about 285 MB; unsolved: the 1,594 BOBILib lists as feasible
#                      or open; all: all 2,654 instances, about 1.45 GB
#   DEST=data          target folder
#   JOBS=4             parallel downloads (at most 4)
#   LOCAL=DIR          an existing BOBILib download (same layout) to copy from first
#
# The paper, its figures and the data package are built in paper/ (paper/Makefile).

PY     ?= python3 -I
SUBSET ?= used
DEST   ?= data
JOBS   ?= 4
LOCAL  ?=

FETCH = $(PY) scripts/fetch_data.py --subset $(SUBSET) --dest $(DEST) $(if $(LOCAL),--local $(LOCAL))

.PHONY: fetch-data verify-data

fetch-data:
	$(FETCH) --jobs $(JOBS)

verify-data:
	$(FETCH) --verify-only
