# make_strict_pdb.sh
awk '
function isatom(l){ return (substr(l,1,6)=="ATOM  " || substr(l,1,6)=="HETATM") }
function elem_from_name(name,   t){
  gsub(/^ +| +$/,"",name)
  if (name ~ /^[0-9]/) name=substr(name,2)
  t=substr(name,1,2)
  if (t ~ /^[A-Z][a-z]$/) return t
  return substr(t,1,1)
}
BEGIN{n=0}
{
  if(!isatom($0)){ print; next }

  rec  = substr($0,1,6)
  name = substr($0,13,4)       # we will RIGHT-justify when printing
  alt  = substr($0,17,1)
  resn = substr($0,18,3)       # keep HID/HIE/HIP if present
  chn  = substr($0,22,1)
  resi = substr($0,23,4)
  icode= substr($0,27,1)

  # read coords numerically to avoid spacing issues
  x = substr($0,31,8)+0
  y = substr($0,39,8)+0
  z = substr($0,47,8)+0

  # clean occ/beta (PQR carryover)
  occ="  1.00"; bfc=" 20.00"

  elem = elem_from_name(name)
  ++n
  printf("%-6s%5d %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6s%6s          %2s\n",
         rec, n, name, alt, resn, chn, resi, icode, x, y, z, occ, bfc, elem)
}' CAD_sanitized.pdb > CAD_strict.pdb

