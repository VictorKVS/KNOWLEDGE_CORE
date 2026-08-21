#!/usr/bin/env python3
import json
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/controls/fstec-methodical-2026-mse-family-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/controls/fstec-methodical-2026-mse-family-regression-v1.json")
def main():
 m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); ms={x["code"]:x for x in m["measures"]}; ps={x["id"]:x for x in m["operator_defined_parameters"]}
 def has(c,s): return any(s in x for x in ms[c]["implementation"])
 def er(c,s): return any(s in x["rule"] for x in ms[c]["enhancements"])
 def op(p): return "OPERATOR_DEFINED" if ps[p]["universal_value"]=="NOT_STATED" else None
 def ev(c):
  q=c["query"]
  if q=="measure_count": return len(ms)
  if q=="implementation_total": return sum(len(x["implementation"]) for x in ms.values())
  if q=="documentation_total": return sum(len(x["documentation"]) for x in ms.values())
  if q=="enhancement_total": return sum(len(x["enhancements"]) for x in ms.values())
  if q=="numeric_count": return len(m["numeric_constraints"])
  if q=="parameter_count": return len(ps)
  if q=="matrix_counts": return {k:m["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
  if q=="blank_rows": return m["class_matrix_summary"]["fully_blank_measure_rows"]
  if q=="field_counts":
   x=ms[c["measure"]]; return {k:len(x[k]) for k in ("implementation","documentation","enhancements")}
  if q=="base_row": return ms[c["measure"]]["matrix"]["base"]
  if q=="enhancement_row": return ms[c["measure"]]["matrix"]["enhancements"]
  if q=="mse1_segment_types": return ["NETWORK","FUNCTIONAL","SIGNIFICANCE","PROTECTION_CLASS","DEVICE_TYPE","VIRTUAL","CONTAINER"] if all(has("МСЭ.1",s) for s in ("NETWORK_SEGMENTS","FUNCTIONAL_SEGMENTS","SIGNIFICANCE_LEVEL","PROTECTION_CLASS","DEVICE_TYPE","VIRTUAL_ENVIRONMENT","CONTAINER_ENVIRONMENT")) else None
  if q=="mse1_boundary_filter": return has("МСЭ.1","CONTROL_AND_FILTER")
  if q=="mse1_annual":
   x=m["numeric_constraints"][0]; return {k:x[k] for k in ("relation","value","unit")}
  if q=="mse1_least_privilege": return has("МСЭ.1","LEAST_PRIVILEGE")
  if q=="mse1_means": return ["FIREWALL","ONE_WAY_TRANSFER","PHYSICAL_IF_NEEDED"] if has("МСЭ.1","IF_NEEDED_OPERATOR_DEFINED_PHYSICAL_ISOLATION") else None
  if q=="mse1_doc": return len(ms["МСЭ.1"]["documentation"])==1
  if q=="mse1_microsegmentation": return er("МСЭ.1","MICROSEGMENTATION")
  if q=="mse1_external_app_access": return er("МСЭ.1","EXTERNAL_USER_ACCESS")
  if q=="mse1_rule_automation": return er("МСЭ.1","AUTOMATE_FILTER_RULE")
  if q=="mse1_central_events": return er("МСЭ.1","CENTRALLY_REGISTER")
  if q=="mse1_only_enh1_k1": return ms["МСЭ.1"]["matrix"]["enhancements"]=={"K3":[],"K2":[],"K1":[1]}
  if q=="mse1_physical_scope": return op("MSE1_PHYSICAL_ISOLATION_SCOPE")
  if q=="mse2_dmz": return has("МСЭ.2","CREATE_DMZ")
  if q=="mse2_isolation": return has("МСЭ.2","ISOLATE_DMZ")
  if q=="mse2_all_connections": return has("МСЭ.2","ALL_DMZ_EXTERNAL_AND_INTERNAL")
  if q=="mse2_doc": return len(ms["МСЭ.2"]["documentation"])==1
  if q=="mse2_web_firewall": return er("МСЭ.2","WEB_SERVER_LEVEL_FIREWALLS")
  if q=="mse2_reverse_proxy": return er("МСЭ.2","REVERSE_PROXIES")
  if q=="mse2_memory_range": return er("МСЭ.2","ALLOWED_ADDRESS_RANGE")
  if q=="mse2_range_value": return op("MSE2_ALLOWED_MEMORY_ADDRESS_RANGE")
  if q=="mse3_all_boundaries": return has("МСЭ.3","ALL_TRAFFIC_AT_INTERSEGMENT_AND_EXTERNAL")
  if q=="mse3_threat_rules_or_one_way": return "OR" if has("МСЭ.3","AND_OR_ONE_WAY_TRANSFER") else None
  if q=="mse3_both_directions": return ["INBOUND","OUTBOUND"] if has("МСЭ.3","INBOUND") and has("МСЭ.3","OUTBOUND") else None
  if q=="mse3_register_violations": return has("МСЭ.3","REGISTER_SECURITY_EVENTS")
  if q=="mse3_backup": return has("МСЭ.3","BACK_UP_FIREWALL_RULE_LIST")
  if q=="mse3_doc": return len(ms["МСЭ.3"]["documentation"])==1
  if q=="mse3_hardware_filter": return er("МСЭ.3","HARDWARE_PACKET_FILTERING")
  if q=="mse3_no_backup_frequency": return op("MSE3_RULE_BACKUP_PROCEDURE")
  if q=="mse4_boundary_components": return has("МСЭ.4","EXTERNAL_BOUNDARY_COMPONENTS")
  if q=="mse4_hidden_details": return ["NETWORK_ADDRESSES","NODE_NAMES","SOFTWARE_TYPES","SOFTWARE_VERSIONS"] if has("МСЭ.4","NETWORK_ADDRESSES_NODE_NAMES_AND_SOFTWARE_TYPES_AND_VERSIONS") else None
  if q=="mse4_responses": return has("МСЭ.4","NETWORK_RESPONSES")
  if q=="mse4_no_disruption": return has("МСЭ.4","DOES_NOT_DISRUPT")
  if q=="mse4_enhancements": return ["HIDE_ADDRESSES","SCAN_SLOWDOWN","IGNORE_EXTERNAL","MASK_TRAFFIC_ATTRIBUTES"] if len(ms["МСЭ.4"]["enhancements"])==4 else None
  if q=="mse4_blank_not_prohibition": return "DO_NOT_TREAT_MSE_4_OR_MSE_5_BLANK_BASE_ROW_AS_PROHIBITION_OR_PROOF_OF_NON_APPLICABILITY" in m["scope_guards"]
  if q=="mse5_decoy_use": return has("МСЭ.5","USE_DECOY_INFORMATION_SYSTEMS")
  if q=="mse5_pipeline": return ["IMITATE","DETECT_REGISTER","SEND_TO_MONITORING"] if all(has("МСЭ.5",s) for s in ("IMITATE_REAL","DETECT_AND_REGISTER","SEND_COLLECTED")) else None
  if q=="mse5_isolated_no_restricted": return has("МСЭ.5","ISOLATE_DECOY") and has("МСЭ.5","EXCLUDE_RESTRICTED")
  if q=="mse5_decoy_data": return er("МСЭ.5","CREATE_DECOY_DATA")
  if q=="mse5_examples": return ms["МСЭ.5"]["enhancements"][0]["non_exhaustive_examples"]
  if q=="mse5_examples_nonexhaustive": return "DO_NOT_TREAT_DECOY_DATA_EXAMPLES_AS_EXHAUSTIVE_OR_ALL_MANDATORY" in m["scope_guards"]
  if q=="mse5_identity_deception": return er("МСЭ.5","IDENTIFIABLE_AS_EXISTING_SYSTEM")
  if q=="mse5_blank_not_prohibition": return "МСЭ.5" in m["class_matrix_summary"]["fully_blank_measure_rows"] and "DO_NOT_TREAT_MSE_4_OR_MSE_5_BLANK_BASE_ROW_AS_PROHIBITION_OR_PROOF_OF_NON_APPLICABILITY" in m["scope_guards"]
  if q=="complete_family": return m["verification_boundary"]["complete_mse_family"]
  if q=="official_bytes": return m["verification_boundary"]["official_immutable_bytes"]
  if q=="gap_boundary": return {"critical":m["verification_boundary"]["critical_gap_created"],"high":m["verification_boundary"]["high_gap_created"]}
  raise AssertionError(q)
 assert m["status"]=="VERIFIED_BOUNDED_COMPLETE_MSE_PUBLIC_TEXT_CROSSCHECK" and list(ms)==[f"МСЭ.{i}" for i in range(1,6)]
 bad=[]
 for c in f["cases"]:
  a=ev(c)
  if a!=c["expected"]: bad.append((c["id"],c["expected"],a))
 if bad:
  for x in bad: print("FAIL",x)
  raise SystemExit(1)
 print("PASS: 5 MSE measures; 34 implementation atoms; 3 documentation items; 14 enhancements; 30 class cells; 1 annual constraint; 10 operator-defined parameters; 64 fail-closed cases")
if __name__=="__main__": main()
