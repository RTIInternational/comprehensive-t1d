# Mapping of economist variables to platform variable:

| Econ Variable | Platform Variable | Notes |
|---|---|---|
| AGE | age_entry |  |
| CVDPRIOR | cvd | has_history(individual, flag, step) |
| DUR_YR00 | diabetes_duration_entry |  |
| EDUCOLL1 | has_secondary_ed |  |
| EDUCOLL2 | has_postsecondary_ed |  |
| MARRIEDCOLL | is_married |  |
| OBSEXREC | male |  |
| RACECOLL | race |  |
| FAMIDDM | family_history_iddm |  |
| FAMMI | family_history_mi |  |
| FAMNIDDM | family_history_niddm |  |
| BP_TX | bp_treatment |  |
| LIP_TX | lipid_treatment |  |
| FBMI | curr_bmi | get_event_in_step(individual, 'bmi', step) |
| FBPD | curr_dbp | get_event_in_step(individual, 'dbp', step) |
| FBPS | curr_sbp | get_event_in_step(individual, 'sbp', step) |
| FCHL | curr_totchol | get_event_in_step(individual, 'totchol', step) |
| FLDL | curr_ldl | get_event_in_step(individual, 'ldl', step) |
| FPULSE | curr_hr | get_event_in_step(individual, 'hr', step) |
| FSMOKES | curr_smoker | get_event_in_step(individual, 'smoker', step) |
| FSTD_INS | curr_insulin_dose | get_event_in_step(individual, 'insulin_dose', step) |
| FTRG | curr_trig | get_event_in_step(individual, 'trig', step) |
| HTCUM | hypertension | has_event(individual, 'hyperstension') |
| LAG_TVAMP | lag_tv_amputation | has_history(individual, 'amputation', step) |
| LAG_TVCSME | lag_tv_csme | has_history(individual, 'csme', step) |
| LAG_TVCVD | lag_tv_cvd | has_acute_event(individual, 'cvd', step) |
| LAG_TVDPN | lag_tv_dpn | has_acute_event(individual, 'dpn', step) |
| LAG_TVESRD | lag_tv_esrd | has_history(individual, 'esrd', step) |
| LAG_TVGFR | lag_tv_gfr | has_history(individual, 'gfr', step) |
| LAG_TVMA | lag_tv_ma | has_history(individual, 'macroalbuminuria', step) |
| LAG_TVMI | lag_tv_mi | has_history(individual, 'microalbuminuria', step) |
| LAG_TVNPDR | lag_tv_nprd | has_history(individual, 'nprd', step) |
| LAG_TVPDR | lag_tv_pdr | has_history(individual, 'pdr', step) |
| LAG_TVULC | lag_tv_ulcer | has_acute_event(individual, 'ulcer', step) |
| TWD_BMI | twd_bmi | time_weighted_risk_factor(individual, 'bmi') |
| TWD_BPD | twd_dbp | time_weighted_risk_factor(individual, 'dbp') |
| TWD_BPS | twd_sbp | time_weighted_risk_factor(individual, 'sbp') |
| TWD_CHL | twd_totchol | time_weighted_risk_factor(individual, 'totchol') |
| TWD_HBA1C | twd_hba1c | time_weighted_risk_factor(individual, 'hba1c') |
| TWD_HDL | twd_hdl | time_weighted_risk_factor(individual, 'hdl') |
| TWD_LDL | twd_ldl | time_weighted_risk_factor(individual, 'ldl') |
| TWD_PULSE | twd_hr | time_weighted_risk_factor(individual, 'hr') |
| TWD_STD_INS | twd_insulin_dose | time_weighted_risk_factor(individual, 'insulin_dose') |
| TWD_TRG | twd_trig | time_weighted_risk_factor(individual, 'trig') |