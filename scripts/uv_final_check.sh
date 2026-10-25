#!/bin/bash
# Final pass over stubborn unverified entries: curl + DoH fallback
OUT=/home/z/my-project/registry_work/checks/uv_final_results.txt
: > "$OUT"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

check_one() {
  local id="$1" name="$2" url="$3"
  local host final code title
  host=$(echo "$url" | sed -E 's#https?://##; s#/.*##')
  # 1) direct curl
  code=$(curl -sk -o /tmp/body_$id.html -w '%{http_code}' -L --max-time 15 --compressed \
    -A "$UA" -H 'Accept: text/html,application/xhtml+xml' --max-redirs 6 "$url" 2>/dev/null)
  if [ -z "$code" ] || [ "$code" = "000" ]; then
    # 2) DoH resolve + --resolve
    ips=$(curl -sk --max-time 8 "https://dns.google/resolve?name=$host&type=A" 2>/dev/null | \
      python3 -c "import sys,json;d=json.load(sys.stdin);print(' '.join(a['data'] for a in d.get('Answer',[]) if a.get('type')==1))" 2>/dev/null)
    if [ -n "$ips" ]; then
      local ip; ip=$(echo $ips | awk '{print $1}')
      code=$(curl -sk -o /tmp/body_$id.html -w '%{http_code}' -L --max-time 15 --compressed \
        -A "$UA" --resolve "$host:443:$ip" --resolve "$host:80:$ip" --max-redirs 6 "$url" 2>/dev/null)
      final="doh:$ip"
    else
      final="NXDOMAIN"
    fi
  else
    final="direct"
  fi
  title=$(python3 -c "
import re,sys
try:
    b=open('/tmp/body_$id.html','rb').read(200000).decode('utf-8','ignore')
    m=re.search(r'<title[^>]*>(.*?)</title>',b,re.S|re.I)
    print(re.sub(r'\s+',' ',m.group(1)).strip()[:100] if m else '')
except: pass" 2>/dev/null)
  echo "$id|$name|$url|code=$code|via=$final|title=$title" >> "$OUT"
  rm -f /tmp/body_$id.html
}
export -f check_one
export UA OUT

cat <<'EOF' > /tmp/uv_list.txt
58|Josh|https://joshapp.com
169|iROKOtv|https://irokotv.com
295|AzTV|https://aztv.az
343|Playeur|https://playeur.com
438|Discover.film|https://discover.film
441|Slow Channel|https://slowchannel.com
1163|Planet Marathi OTT|https://planetmarathi.com/
1166|Atrangii|https://www.atrangii.com/
1172|Toffee|https://www.toffee.com.bd/
1312|Bstation|https://www.bstation.com
1355|UpLive|https://www.uplive.com
1370|smash.|https://smash.media
1371|Anime Times|https://animetimestv.com
1397|Trace Play|https://traceplay.tv
1418|Filmatique|https://www.filmatique.tv
1438|GoPlay.bg|https://goplay.bg
1440|BrutX|https://www.brutx.com
B5-023|Stievie|https://www.stievie.be
B5-071|TVA+|https://www.tvaplus.ca
B5-077|Cineplex Store|https://cineplexstore.com
B5-078|Highball.TV|https://highball.tv
B5-122|KHL|https://www.khl.ru
B5-131|EFL iFollow|https://ifollow.co.uk
EOF

xargs -P 8 -I{} bash -c 'IFS="|" read -r id name url <<< "{}"; check_one "$id" "$name" "$url"' < /tmp/uv_list.txt
sort -t'|' -k1 "$OUT" -o "$OUT"
cat "$OUT"
