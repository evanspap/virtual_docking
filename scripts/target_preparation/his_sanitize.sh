#!/usr/bin/env bash
# Usage: bash his_sanitize.sh INPUT.pqr > OUTPUT.pdb
# Cleans PQR/PDB, makes HIS tautomers explicit (HID/HIE/HIP), renumbers atoms.

INPUT="${1:-}"
[ -f "$INPUT" ] || { echo "Input file not found"; exit 1; }

awk '
function isatom(l){return (substr(l,1,6)=="ATOM  " || substr(l,1,6)=="HETATM")}
function elem_from_name(name,   t){
  gsub(/^ +| +$/,"",name)
  if (name ~ /^[0-9]/) name=substr(name,2)
  t=substr(name,1,2)
  if (t ~ /^[A-Z][a-z]$/) return t
  return substr(t,1,1)
}
function key(chn, resi){ gsub(/ /,"",resi); return chn ":" resi }

# First pass: detect which HIS residues have HD1 / HE2
FNR==NR{
  if(!isatom($0)) next
  resn=substr($0,18,3)
  if(resn!="HIS" && resn!="HID" && resn!="HIE" && resn!="HIP") next
  name=substr($0,13,4)
  chn=substr($0,22,1)
  resi=substr($0,23,4)
  k=key(chn,resi)
  if(name ~ /^ HD1$/) hasHD1[k]=1
  if(name ~ /^ HE2$/) hasHE2[k]=1
  next
}

# Second pass: print sanitized PDB
{
  if(!isatom($0)){ print; next }

  rec  = substr($0,1,6)
  name = substr($0,13,4)
  alt  = substr($0,17,1)
  resn = substr($0,18,3)
  chn  = substr($0,22,1)
  resi = substr($0,23,4)
  icode=substr($0,27,1)

  x = substr($0,31,8)+0
  y = substr($0,39,8)+0
  z = substr($0,47,8)+0

  occ="  1.00"; bfc=" 20.00"

  k=key(chn,resi)
  taut=resn
  if(resn=="HIS"){
    if(hasHD1[k] && !hasHE2[k]) taut="HID"
    else if(hasHE2[k] && !hasHD1[k]) taut="HIE"
    else if(hasHD1[k] && hasHE2[k]) taut="HIP"
    else taut="HIE"
  }

  # Drop inconsistent ring H
  if(taut=="HID" && name ~ /^ HE2$/) next
  if(taut=="HIE" && name ~ /^ HD1$/) next
  if(taut!="HIP" && name ~ /^ H[DE][12]$/ && !( (taut=="HID"&&name~" HD1$") || (taut=="HIE"&&name~" HE2$") )) next

  elem=elem_from_name(name)
  ++n
  printf("%-6s%5d %-4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6s%6s          %2s\n",
         rec, n, name, alt, taut, chn, resi, icode, x, y, z, occ, bfc, elem)
}
' "$INPUT" "$INPUT"

