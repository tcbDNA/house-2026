#!/bin/bash
# usage: cdx_state.sh <url-prefix-without-scheme> <from YYYYMMDD> <to YYYYMMDD> <outfile>
# Lists every Wayback capture under the prefix in the window (timestamp original statuscode length). Retries on errors.
pfx="$1"; from="$2"; to="$3"; out="$4"
for i in 1 2 3 4 5 6; do
  curl -s -m 240 "https://web.archive.org/cdx/search/cdx?url=${pfx}&matchType=prefix&from=${from}&to=${to}&fl=timestamp,original,statuscode,length&limit=20000" -o "$out.part"
  if [ -s "$out.part" ] && ! grep -q -i -E '<html|Gateway|Temporarily Offline' "$out.part"; then mv "$out.part" "$out"; echo "OK $pfx $(wc -l < "$out")"; exit 0; fi
  if [ -f "$out.part" ] && [ ! -s "$out.part" ]; then mv "$out.part" "$out"; echo "EMPTY $pfx"; exit 0; fi
  sleep $((i*15))
done
echo "FAIL $pfx"; rm -f "$out.part"; exit 1
