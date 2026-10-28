#!/bin/bash
# usage: fetch_feeds.sh <rcp_feeds dir> <race id>...
# Saves https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json as served (gzip transfer decoded).
d="$1"; shift
[ -f "$d/_fetch_log.tsv" ] || printf 'fetched_utc\trace_id\thttp\tbytes\tfile\turl\n' > "$d/_fetch_log.tsv"
for id in "$@"; do
  f="race_${id}_polling_data_2026-10-28.json"; u="https://orig.realclearpolitics.com/poll/race/${id}/polling_data.json"
  [ -s "$d/$f" ] && continue
  code=$(curl -s --compressed -m 60 --retry 3 -A "Mozilla/5.0" -o "$d/$f" -w '%{http_code}' "$u")
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$id" "$code" "$(wc -c < "$d/$f" | tr -d ' ')" "$f" "$u" >> "$d/_fetch_log.tsv"
  if [ "$code" != "200" ]; then rm -f "$d/$f"; echo "FAIL $id $code"; else echo "OK $id"; fi
  sleep 1
done
