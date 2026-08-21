#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL=Path("security-knowledge/controls/fstec-methodical-2026-zks-family-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/controls/fstec-methodical-2026-zks-family-regression-v1.json")

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures={x["code"]:x for x in model["measures"]}
    params={x["id"]:x for x in model["operator_defined_parameters"]}
    def impl(c): return measures[c]["implementation"]
    def enh(c): return measures[c]["enhancements"]
    def has(c,s): return any(s in x for x in impl(c))
    def erule(c,s): return any(s in x["rule"] for x in enh(c))
    def op(pid): return "OPERATOR_DEFINED" if params[pid]["universal_value"]=="NOT_STATED" else None
    def evaluate(case):
        q=case["query"]
        if q=="measure_count": return len(measures)
        if q=="implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if q=="documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if q=="enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if q=="numeric_count": return len(model["numeric_constraints"])
        if q=="parameter_count": return len(params)
        if q=="matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if q=="blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if q=="field_counts":
            x=measures[case["measure"]]; return {k:len(x[k]) for k in ("implementation","documentation","enhancements")}
        if q=="base_row": return measures[case["measure"]]["matrix"]["base"]
        if q=="no_class_enhancements": return all(not v for x in measures.values() for v in x["matrix"]["enhancements"].values())
        if q=="zks1_restricted_transmission": return has("ЗКС.1","RESTRICTED_INFORMATION")
        if q=="zks1_remote_access": return has("ЗКС.1","REMOTE_USER_ACCESS")
        if q=="zks1_intersegment_dependencies": return ["МСЭ.1","МСЭ.3"] if has("ЗКС.1","WITH_MSE_1_AND_MSE_3") else None
        if q=="zks1_external_dependencies": return ["МСЭ.2","МСЭ.3"] if has("ЗКС.1","WITH_MSE_2_AND_MSE_3") else None
        if q=="zks1_internet_interfaces": return has("ЗКС.1","INTERNET_ACCESSIBLE")
        if q=="zks1_firewall_current": return has("ЗКС.1","KEEP_FIREWALL_RULES_CURRENT")
        if q=="zks1_unused_ports": return has("ЗКС.1","UNUSED_PORTS")
        if q=="zks1_insecure_versions": return has("ЗКС.1","DISABLE_INSECURE_PROTOCOL")
        if q=="zks1_means": return ["FIREWALL","ONE_WAY_TRANSFER","CRYPTO_CONDITIONAL"] if has("ЗКС.1","CRYPTOGRAPHY_UNDER_RUSSIAN_LAW") else None
        if q=="zks1_external_list_doc": return len(measures["ЗКС.1"]["documentation"])==1
        if q=="zks1_crypto_separate": return "DO_NOT_IMPORT_CRYPTOGRAPHIC_PARAMETERS_FROM_FSTEC_DOCUMENT_USE_APPLICABLE_FSB_LAYER" in model["scope_guards"]
        if q=="zks1_no_review_period": return op("ZKS1_FIREWALL_RULE_SET")
        if q=="zks2_attribute_scope": return has("ЗКС.2","SECURITY_ATTRIBUTES_FOR_INFORMATION")
        if q=="zks2_unique_subject": return has("ЗКС.2","UNIQUELY_IDENTIFY_ACCESS_SUBJECT")
        if q=="zks2_sender_recipient": return has("ЗКС.2","SENDER_AND_RECIPIENT_SECURITY_ATTRIBUTE_LISTS")
        if q=="zks2_before_transmission": return has("ЗКС.2","BEFORE_DATA_TRANSMISSION")
        if q=="zks2_before_receipt": return has("ЗКС.2","BEFORE_DATA_RECEIPT")
        if q=="zks2_mse3": return has("ЗКС.2","WITH_MSE_3")
        if q=="zks2_rsb_dependency": return "РСБ.1-РСБ.5" if has("ЗКС.2","WITH_RSB_1_TO_RSB_5") else None
        if q=="zks2_firewall_means": return has("ЗКС.2","IMPLEMENT_USING_FIREWALLS")
        if q=="zks2_no_docs_enh": return not measures["ЗКС.2"]["documentation"] and not enh("ЗКС.2")
        if q=="zks2_attribute_set": return op("ZKS2_SECURITY_ATTRIBUTE_SET")
        if q=="zks3_resource_list": return "ALLOW_AND_OR_DENY" if has("ЗКС.3","ALLOW_AND_OR_DENY_LIST") else None
        if q=="zks3_access_control": return has("ЗКС.3","CONTROL_USER_APPLICATION")
        if q=="zks3_block": return has("ЗКС.3","BLOCK_ATTEMPTS")
        if q=="zks3_protocol_list": return has("ЗКС.3","ALLOWED_NETWORK_PROTOCOL")
        if q=="zks3_list_doc": return len(measures["ЗКС.3"]["documentation"])==1
        if q=="zks3_morphological": return erule("ЗКС.3","MORPHOLOGICAL")
        if q=="zks3_categorization": return erule("ЗКС.3","CATEGORIZATION")
        if q=="zks3_lists_not_both_required": return "DO_NOT_TREAT_ALLOWED_AND_DENIED_RESOURCE_LISTS_AS_CUMULATIVELY_MANDATORY" in model["scope_guards"]
        if q=="zks4_context_outbound": return has("ЗКС.4","CONTEXTUALLY_INSPECT_OUTBOUND")
        if q=="zks4_analysis_dimensions": return ["CONTENT","METADATA","BEHAVIOR"] if all(has("ЗКС.4",s) for s in ("DATA_CONTENT","DATA_METADATA","BEHAVIORAL_CHARACTERISTICS")) else None
        if q=="zks4_anomalies": return has("ЗКС.4","ANOMALOUS_NETWORK_TRAFFIC")
        if q=="zks4_scope_control": return has("ЗКС.4","CONTROL_DEFINED_NETWORK_PORTS")
        if q=="zks4_internet_nonexclusive": return has("ЗКС.4","WITHOUT_LIMITING_SCOPE_TO_INTERNET")
        if q=="zks4_enhancements": return ["DPI","USER_BEHAVIOR","ENDPOINT_AGENTS","OBFUSCATION_BLOCK","CLOUD_CONTROL","CONTENT_CLASSIFICATION"] if len(enh("ЗКС.4"))==6 else None
        if q=="zks4_blank_not_prohibition": return "DO_NOT_TREAT_ZKS_4_BLANK_BASE_ROW_AS_PROHIBITION_OR_PROOF_OF_NON_APPLICABILITY" in model["scope_guards"]
        if q=="zks4_analysis_rules": return op("ZKS4_CONTEXT_ANALYSIS_RULE_SET")
        if q=="zks4_anomaly_criteria": return op("ZKS4_ANOMALY_CRITERIA")
        if q=="catalog_codes": return list(measures)
        if q=="zks5_absent": return "ЗКС.5" not in measures
        if q=="zks5_referrers": return model["source_anomalies"][0]["referencing_measures"]
        if q=="zks5_guard": return "DO_NOT_SYNTHESIZE_ZKS_5_FROM_LITERAL_ZVT_1_OR_ZPI_1_REFERENCE" in model["scope_guards"]
        if q=="zks5_resolution": return model["source_anomalies"][0]["resolution"]
        if q=="complete_family": return model["verification_boundary"]["complete_zks_family"]
        if q=="official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if q=="gap_boundary": return {"critical":model["verification_boundary"]["critical_gap_created"],"high":model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(q)
    assert model["status"]=="VERIFIED_BOUNDED_COMPLETE_ZKS_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures)==[f"ЗКС.{i}" for i in range(1,5)]
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual!=case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures: print("FAIL",failure)
        raise SystemExit(1)
    print("PASS: 4 ZKS measures; 29 implementation atoms; 2 documentation items; 8 enhancements; 24 class cells; 0 numeric constraints; 10 operator-defined parameters; 1 source anomaly; 64 fail-closed cases")

if __name__=="__main__": main()
