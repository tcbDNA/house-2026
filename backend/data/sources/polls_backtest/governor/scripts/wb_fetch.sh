#!/bin/bash
# usage: wb_fetch.sh <timestamp> <original_url> <outfile> [fetchlog.tsv]
# Fetch the raw Wayback capture (id_ suffix), no redirects followed; require HTTP 200.
# Transfer gzip is decoded by curl (--compressed); if the body is still gzip, it is gunzipped.
# Appends: fetched_utc, ts, memento-datetime, orig last-modified, orig date, bytes, file, url to fetchlog.
# Nothing in the downloaded file is executed.
ts="$1"; url="$2"; out="$3"; log="${4:-/dev/null}"
hdr="$(mktemp)"
code=$(curl -s --compressed -m 180 --retry 4 --retry-delay 5 -A "Mozilla/5.0 (research archive fetch)" -D "$hdr" -o "$out.part" -w '%{http_code}' "https://web.archive.org/web/${ts}id_/${url}")
rc=$?
if [ $rc -ne 0 ] || [ "$code" != "200" ]; then echo "FAIL rc=$rc http=$code $ts $url" >&2; rm -f "$out.part" "$hdr"; exit 1; fi
if [ "$(head -c 2 "$out.part" | xxd -p)" = "1f8b" ]; then gunzip -c "$out.part" > "$out" && rm -f "$out.part"; else mv "$out.part" "$out"; fi
md=$(grep -i '^memento-datetime:' "$hdr" | cut -d' ' -f2- | tr -d '\r')
lm=$(grep -i '^x-archive-orig-last-modified:' "$hdr" | cut -d' ' -f2- | tr -d '\r')
od=$(grep -i '^x-archive-orig-date:' "$hdr" | cut -d' ' -f2- | tr -d '\r')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$ts" "$md" "$lm" "$od" "$(wc -c < "$out" | tr -d ' ')" "$(basename "$out")" "$url" >> "$log"
rm -f "$hdr"
echo "OK $ts $(wc -c < "$out" | tr -d ' ') $(basename "$out") lastmod=[$lm]"
