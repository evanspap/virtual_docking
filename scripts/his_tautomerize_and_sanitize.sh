#!/usr/bin/env bash
# Sanitize PDB/PQR -> strict PDB; auto-rename HIS->HID/HIE based on HD1/HE2;
# keep only the consistent ring-H; renumber; set Element column.
# Usage: bash his_tautomerize_and_sanitize.sh INPUT.pqr > OUT.pdb

set -euo pipefail
IN="${1:-}"
[ -f "$IN" ] || { echo "Input not found"; exit 1; }

# First pass: detect, by residue, whether we have HD1 or HE2
awk '
function isatom(l){return (substr(l,1,6)=="ATOM  " || substr(l,1,6)=="HETATM")}
function key(chn, resi){ gsub(/ /,"",resi); return chn ":" resi }

{
  if(!isatom($0)){ next }

  rec  = substr($0,1,6)
  name = substr($0,13,4)
  chn  = substr($0,22,1)
  resi = substr($0,23,4)

  # PQR sometimes has shifted fields; tolerate leading blanks
  # Detect HIS residue name from columns 18-20 if possible
  resn = substr($0,18,3)
  if (resn!="HIS" && resn!="HID" && resn!="HIE" && resn!="HIP") next

  k = key(chn,resi)
  if (name ~ /^ HD1$/) hasHD1[k]=1
  if (name ~ /^ HE2$/) hasHE2[k]=1
}
END{
  for (k in hasHD1) print "K HD1 " k
  for (k in hasHE2) print "K HE2 " k
}' "$IN" | awk '
{
  # build two sets: hd1[k]=1 or he2[k]=1
  if($2=="HD1"){hd1[$3]=1}else if($2=="HE2"){he2[$3]=1}
}
BEGIN{FS=OFS=""}
{
  # store to /dev/null; this block only builds arrays via awk variables
}
END{
  # Re-run file and actually print sanitized PDB
}' | cat >/dev/null

# Second pass: produce strict PDB with correct tautomer names
awk -v in="$IN" '
function isatom(l){return (substr(l,1,6)=="ATOM  " || substr(l,1,6)=="HETATM")}
function elem_from_name(name,   t){
  gsub(/^ +| +$/,"",name)
  if (name ~ /^[0-9]/) name=substr(name,2)
  t=substr(name,1,2)
  if (t ~ /^[A-Z][a-z]$/) return t
  return substr(t,1,1)
}
function key(chn, resi){ gsub(/ /,"",resi); return chn ":" resi }

BEGIN{
  # Build maps of HD1/HE2 presence from first pass
  while ((getline L < in) > 0) {
    if(!isatom(L)) continue
    resn = substr(L,18,3)
    if (resn!="HIS" && resn!="HID" && resn!="HIE" && resn!="HIP") continue
    name = substr(L,13,4)
    chn  = substr(L,22,1)
    resi = substr(L,23,4)
    k = key(chn,resi)
    if (name ~ /^ HD1$/) hasHD1[k]=1
    if (name ~ /^ HE2$/) hasHE2[k]=1
  }
  close(in)
  n=0
}
{
  if(!isatom($0)){ print; next }

  rec  = substr($0,1,6)
  name = substr($0,13,4)
  alt  = substr($0,17,1)
  resn = substr($0,18,3)
  chn  = substr($0,22,1)
  resi = substr($0,23,4)
  icode= substr($0,27,1)

  # Coordinates: read as numeric to avoid misalignment artifacts (PQR->PDB)
  x = substr($0,31,8)+0
  y = substr($0,39,8)+0
  z = substr($0,47,8)+0

  # For PQR inputs, the occ/beta columns are charges/radii; reset to sane defaults
  occ="  1.00"; bfc=" 20.00"

  k = key(chn,resi)

  # Decide tautomer
  t = resn
  if (resn=="HIS") {
    if (hasHD1[k] && !hasHE2[k]) t="HID"
    else if (hasHE2[k] && !hasHD1[k]) t="HIE"
    else if (hasHD1[k] && hasHE2[k]) t="HIP"          # both present → cationic
    else t="HIE"                                      # default if ambiguous
  } else if (resn=="HID" || resn=="HIE" || resn=="HIP") {
    t = resn
  }

  # Keep only consistent ring-H for that tautomer
  if (t=="HID" && name ~ /^ HE2$/) next
  if (t=="HIE" && name ~ /^ HD1$/) next
  # For HIP keep both; for neutral keep ring H that exists; drop ring Hs if unknown
  if (t!="HIP" && name ~ /^ H[DE][12]$/ && !( (t=="HID"&&name~" HD1$") || (t=="HIE"&&name~" HE2$") )) next

  elem = elem_from_name(name)
  n++
  printf("%-6s%5d %-4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6s%6s          %2s\n",
         rec, n, name, alt, t, chn, resi, icode, x, y, z, occ, bfc, elem)
}' "$IN"

