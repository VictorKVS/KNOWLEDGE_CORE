#!/usr/bin/env python3
import json
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/controls/fstec-methodical-2026-zoo-family-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/controls/fstec-methodical-2026-zoo-family-regression-v1.json")
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
  if q=="zoo1_dmz": return has("ЗОО.1","DMZ_CONFORMING_TO_MSE_2")
  if q=="zoo1_filter_locations": return has("ЗОО.1","AT_OR_BEFORE_DMZ")
  if q=="zoo1_delivery_options": return ["OPERATOR","PROVIDER","CARRIER","SPECIALIZED_SERVICE"] if has("ЗОО.1","OPERATOR_PROVIDER_CARRIER_AND_OR_SPECIALIZED") else None
  if q=="zoo2_post_detection": return has("ЗОО.2","AFTER_DENIAL_OF_SERVICE_ATTACK_DETECTION")
  if q=="zoo2_layers": return ["NETWORK","TRANSPORT","APPLICATION"] if all(has("ЗОО.2",s) for s in ("NETWORK_AND_TRANSPORT","APPLICATION_LAYER")) else None
  if q=="zoo2_matrix_current": return has("ЗОО.2","MAINTAIN_CURRENT_TRANSPORT_LAYER")
  if q=="zoo2_allowlist": return has("ЗОО.2","APPLY_ALLOWLISTS")
  if q=="zoo2_geoip_conditional": return has("ЗОО.2","CONDITIONALLY_EXCLUDE_NON_RUSSIAN")
  if q=="zoo2_docs": return len(ms["ЗОО.2"]["documentation"])==3
  if q=="zoo2_retention":
   x=next(x for x in m["numeric_constraints"] if x["id"]=="ZOO2_ATTACK_INFORMATION_RETENTION"); return {k:x[k] for k in ("relation","value","unit")}
  if q=="zoo2_retention_fields": return has("ЗОО.2","APPLICATION_LAYER") and any("RETAIN_DDOS_ATTACK" in x for x in ms["ЗОО.2"]["documentation"])
  if q=="zoo2_enh1_continuous": return er("ЗОО.2","CONTINUOUSLY")
  if q=="zoo2_enh2_tls": return er("ЗОО.2","TLS_TRAFFIC_ANALYSIS")
  if q=="zoo2_only_enh1_k1": return ms["ЗОО.2"]["matrix"]["enhancements"]=={"K3":[],"K2":[],"K1":[1]}
  if q=="zoo2_matrix_parameter": return op("ZOO2_COMMUNICATION_MATRIX")
  if q=="zoo3_resource_metrics": return has("ЗОО.3","CPU_MEMORY_AND_NETWORK_INTERFACE")
  if q=="zoo3_connection_metrics": return has("ЗОО.3","CONCURRENT_CONNECTION_COUNT")
  if q=="zoo3_app_metrics": return has("ЗОО.3","APPLICATION_LAYER_REQUEST_COUNT")
  if q=="zoo3_error_metrics": return has("ЗОО.3","COUNT_AND_TYPES")
  if q=="zoo3_continuous_events": return has("ЗОО.3","CONTINUOUSLY_REGISTER")
  if q=="zoo3_docs": return len(ms["ЗОО.3"]["documentation"])==2
  if q=="zoo3_provider_metrics": return er("ЗОО.3","CORE_METRICS_AND_EFFECTIVENESS")
  if q=="zoo3_internet_monitor": return er("ЗОО.3","TOOLS_LOCATED_ON_THE_INTERNET")
  if q=="zoo3_kpi_parameter": return op("ZOO3_KPI_SET")
  if q=="zoo4_multi_provider": return has("ЗОО.4","MULTIPLE_INTERNET_PROVIDERS")
  if q=="zoo4_simultaneous": return has("ЗОО.4","RECEIVE_TRAFFIC_SIMULTANEOUSLY")
  if q=="zoo4_provider_selection": return has("ЗОО.4","SELECT_PROVIDER")
  if q=="zoo4_vertical": return has("ЗОО.4","VERTICAL_SCALING")
  if q=="zoo4_horizontal": return er("ЗОО.4","HORIZONTAL_SCALING")
  if q=="zoo4_geo_conditional": return er("ЗОО.4","CONDITIONALLY_DISTRIBUTE")
  if q=="zoo4_blank_not_prohibition": return "DO_NOT_TREAT_ZOO_4_BLANK_ROW_OR_ZOO_6_K3_BLANK_CELL_AS_PROHIBITION_OR_PROOF_OF_NON_APPLICABILITY" in m["scope_guards"]
  if q=="zoo5_tcp_limit": return has("ЗОО.5","MAXIMUM_CONCURRENT_TCP")
  if q=="zoo5_dns_limit": return has("ЗОО.5","DNS_SERVER_RESPONSE_RATE")
  if q=="zoo5_request_limit": return has("ЗОО.5","APPLICATION_REQUESTS_PER_SECOND")
  if q=="zoo5_monitor": return has("ЗОО.5","DETECT_ANOMALOUS_BEHAVIOR")
  if q=="zoo5_values": return [op("ZOO5_MAX_TCP_CONNECTIONS_PER_IP"),op("ZOO5_DNS_RESPONSE_RATE"),op("ZOO5_MAX_APPLICATION_REQUESTS_PER_SECOND_PER_IP")]
  if q=="zoo6_provider_factor": return next(x["value"] for x in m["numeric_constraints"] if x["id"]=="ZOO6_PROVIDER_BANDWIDTH_RESERVE")
  if q=="zoo6_processing_factor": return next(x["value"] for x in m["numeric_constraints"] if x["id"]=="ZOO6_PROCESSING_RESERVE")
  if q=="zoo6_internal_factor": return next(x["value"] for x in m["numeric_constraints"] if x["id"]=="ZOO6_INTERNAL_PATH_RESERVE_ENHANCEMENT_1")
  if q=="zoo6_operator_elements": return op("ZOO6_PROCESSING_RESERVE_ELEMENT_SET")
  if q=="zoo6_high_performance": return er("ЗОО.6","HIGH_PERFORMANCE_NETWORK_HARDWARE")
  if q=="zoo6_examples": return ms["ЗОО.6"]["enhancements"][1]["non_exhaustive_examples"]
  if q=="zoo6_examples_nonexhaustive": return "DO_NOT_TREAT_HIGH_PERFORMANCE_NETWORK_TECHNOLOGY_EXAMPLES_AS_EXHAUSTIVE" in m["scope_guards"]
  if q=="zoo6_k3_blank": return ms["ЗОО.6"]["matrix"]["base"]=={"K3":"BLANK","K2":"PLUS","K1":"PLUS"}
  if q=="no_invented_limits": return "DO_NOT_INVENT_TCP_DNS_REQUEST_RATE_OR_OTHER_LOAD_LIMITS" in m["scope_guards"]
  if q=="complete_family": return m["verification_boundary"]["complete_zoo_family"]
  if q=="official_bytes": return m["verification_boundary"]["official_immutable_bytes"]
  if q=="gap_boundary": return {"critical":m["verification_boundary"]["critical_gap_created"],"high":m["verification_boundary"]["high_gap_created"]}
  raise AssertionError(q)
 assert m["status"]=="VERIFIED_BOUNDED_COMPLETE_ZOO_PUBLIC_TEXT_CROSSCHECK" and list(ms)==[f"ЗОО.{i}" for i in range(1,7)]
 bad=[]
 for c in f["cases"]:
  a=ev(c)
  if a!=c["expected"]: bad.append((c["id"],c["expected"],a))
 if bad:
  for x in bad: print("FAIL",x)
  raise SystemExit(1)
 print("PASS: 6 ZOO measures; 22 implementation atoms; 5 documentation items; 8 enhancements; 36 class cells; 4 numeric constraints; 11 operator-defined parameters; 64 fail-closed cases")
if __name__=="__main__": main()
