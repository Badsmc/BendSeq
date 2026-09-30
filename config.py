# BendSeq/config.py

SEQUENCE_CONFIG = {
    "time_budget_stage2": 5.0,  # seconds for fast search
    "time_budget_stage3": 15.0, # seconds for physical dfs
    
    # Penalties for scoring
    "penalty_base": 1.0,
    "penalty_flip": 5.0,
    "penalty_rotation": 2.0,
    "penalty_tool_change": 10.0,
    "penalty_tool_length": 1.0,
    "penalty_backgauge": 3.0,
    "penalty_feature": 1.0,
    "penalty_contact": 2.0,
    
    # Simulation defaults
    "anim_steps_per_bend": 20,
    "anim_step_delay_ms": 50,
    "anim_retract_distance": 50.0,
    
    # Defaults
    "k_factor_default": 0.5,
    "collision_margin": 0.1,
    
    # Toggles
    "enable_occ_fold_fallback": False,
}
