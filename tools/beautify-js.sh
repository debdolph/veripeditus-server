#!/bin/mksh

find ./src/ -iname "*.js" -print0 |
    while IFS= read -r -d '' f; do
    	t=$(mktemp)
    	cat "$f" >"$t"
    	{ js_beautify "$t"; echo; } >"$f"
    	rm -f "$t"
    done
