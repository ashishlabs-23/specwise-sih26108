from app.storage.repository import get_repository
repo = get_repository()
std_map = {s.standard_id: s for s in repo.standards}

for sid in ['IS 14220:2018', 'IS 8034:2018']:
    s = std_map.get(sid)
    if not s:
        print(sid + ': NOT FOUND')
        continue
    role = getattr(s, 'standard_role', 'UNSET')
    pt = getattr(s, 'product_terms', [])
    at = getattr(s, 'application_terms', [])
    ex = getattr(s, 'exclusion_terms', [])
    print('--- ' + sid + ' ---')
    print('  standard_role    = ' + str(role))
    print('  product_terms    = ' + str(pt))
    print('  application_terms= ' + str(at))
    print('  exclusion_terms  = ' + str(ex))
    print('  keywords         = ' + str(s.keywords))
    print('  evidence_ids     = ' + str(s.evidence_ids))
    print()

# Also check the QCO evidence record
print('--- QCO EVIDENCE ---')
for e in repo.evidence:
    if 'QCO' in e.evidence_id or 'qco' in e.evidence_id.lower():
        print('evidence_id: ' + e.evidence_id)
        print('source_id:   ' + e.source_id)
        print('text:        ' + e.text)
        print('verified:    ' + str(e.verified))
        print()
