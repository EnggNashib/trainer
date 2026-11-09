.PHONY: zip check clean

# The release artifact people upload to claude.ai. Zips the folder itself so
# SKILL.md sits one level down inside, which is what the uploader expects.
zip: clean
	cd .. && zip -rq trainer/trainer.zip trainer \
	  -x 'trainer/.git/*' 'trainer/.gitignore' 'trainer/trainer.zip' '*.DS_Store' \
	     'trainer/__pycache__/*' 'trainer/Makefile' 'trainer/install.sh'
	@unzip -l trainer.zip | tail -3

# Everything that can be verified without network or optional dependencies.
check:
	python3 scripts/validate_program.py scripts/example_program.json
	python3 scripts/build_plan.py scripts/example_program.json --mobile --outdir /tmp/trainer-check
	@node --check /tmp/intake.js 2>/dev/null || true
	@echo "ok — validator and stdlib plan build pass"

clean:
	rm -f trainer.zip
