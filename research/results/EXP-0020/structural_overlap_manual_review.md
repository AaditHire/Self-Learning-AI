# Phase 2B structural-overlap manual review

Reviewed: 2026-09-21, before any Phase 2B gradient step.

Decision: **PASS FOR FREEZE**. No reviewed pair is the same semantic mapping, a renamed/literal-only variant, or a retained prior evaluation task. Similarity flags below are attributable to the deliberately small GOCO grammar, required input scaffolding, or broad control-flow shape. All retained train/evaluation pairs have distinct algorithm labels, lineages, structural signatures, and semantic-operation labels. No normalized-code pair reaches the predeclared 0.98 rejection threshold. The legacy sealed Phase 1 holdout was not opened.

## Automated gate summary

- Training targets: 200/200 verified; failures: 0.
- Confirmatory references: 128/128 verified; failures: 0.
- Exact prompt reuse across train/evaluation: 0.
- Exact train/evaluation algorithm, lineage, structural-signature, and semantic-operation overlaps: 0 each.
- Train/evaluation prompt flags at 0.70: 4.
- Train/evaluation normalized-code flags at 0.85: 81; rejects at 0.98: 0.
- Exact AST-proxy flags: 25.
- Distance buckets: {'far': 3, 'medium': 44, 'near': 81}.
- Prior consumed-suite prompt flags at 0.70: 0; normalized-code flags at 0.90: 84.
- Prior normalized-code pairs at or above 0.98: 0.

## Prompt flags reviewed

| evaluation | nearest training | similarity | evaluation algorithm | training algorithm | resolution |
|---|---|---|---|---|---|
| P2B-EVAL-LP01 | P2B-TR-LP-LINEAR_TERM_SUM-04 | 0.727 | confirm_fourth_power_sum | linear_term_sum_4 | retain: different mapping |
| P2B-EVAL-LP05 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.700 | confirm_bilinear_index_sum | linear_term_sum_1 | retain: different mapping |
| P2B-EVAL-AR10 | P2B-TR-AR-WEIGHTED_FOUR-05 | 0.700 | confirm_alternating_sum | weighted_four_5 | retain: different mapping |
| P2B-EVAL-AR14 | P2B-TR-AR-WEIGHTED_FOUR-04 | 0.737 | confirm_pair_products | weighted_four_4 | retain: different mapping |

## Normalized-code flags reviewed

| evaluation | nearest training | similarity | evaluation algorithm | training algorithm | resolution |
|---|---|---|---|---|---|
| P2B-EVAL-EV04 | P2B-TR-EV-DIFFERENCE_OF_SQUARES-01 | 0.899 | confirm_mass_speed_polynomial | difference_of_squares_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV05 | P2B-TR-EV-DIFFERENCE_OF_SQUARES-01 | 0.853 | confirm_hours_minutes | difference_of_squares_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV06 | P2B-TR-EV-CEILING_SCALE-01 | 0.922 | confirm_sqrt_shift | ceiling_scale_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV08 | P2B-TR-EV-DIFFERENCE_OF_SQUARES-01 | 0.903 | confirm_affine_remainder | difference_of_squares_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV10 | P2B-TR-EV-TRIPLE_PRODUCT_ADJUST-01 | 0.908 | confirm_trapezoid_area | triple_product_adjust_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV11 | P2B-TR-EV-TRIPLE_PRODUCT_ADJUST-01 | 0.935 | confirm_mean_four | triple_product_adjust_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV12 | P2B-TR-EV-DIFFERENCE_OF_SQUARES-01 | 0.853 | confirm_squared_origin_distance | difference_of_squares_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV14 | P2B-TR-EV-DIFFERENCE_OF_SQUARES-01 | 0.895 | confirm_percentage_of | difference_of_squares_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-EV16 | P2B-TR-EV-QUOTIENT_SHIFT-01 | 0.866 | confirm_quartic_polynomial | quotient_shift_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD01 | P2B-TR-EV-TRIPLE_PRODUCT_ADJUST-01 | 0.853 | confirm_three_number_max | triple_product_adjust_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD02 | P2B-TR-CD-PARITY_SIGN-01 | 0.942 | confirm_grade_band | parity_sign_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD03 | P2B-TR-CD-EITHER_DIVISOR-01 | 0.880 | confirm_leap_proxy | either_divisor_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD08 | P2B-TR-CD-PARITY_SIGN-01 | 0.912 | confirm_exclusive_range | parity_sign_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD10 | P2B-TR-CD-SMALLER_WITH_TIE-01 | 0.864 | confirm_closest_to_zero | smaller_with_tie_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD12 | P2B-TR-CD-EITHER_DIVISOR-01 | 0.871 | confirm_odd_in_window | either_divisor_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CD15 | P2B-TR-CD-EITHER_DIVISOR-01 | 0.880 | confirm_bounded_divisible | either_divisor_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP01 | P2B-TR-LP-CUBIC_OFFSET_SUM-01 | 0.934 | confirm_fourth_power_sum | cubic_offset_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP02 | P2B-TR-LP-NONMULTIPLE_COUNT-01 | 0.952 | confirm_odd_counter | nonmultiple_count_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP03 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.974 | confirm_union_divisor_sum | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP04 | P2B-TR-LP-NONMULTIPLE_COUNT-01 | 0.944 | confirm_conditional_product | nonmultiple_count_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP05 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.938 | confirm_bilinear_index_sum | linear_term_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP06 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.944 | confirm_multiple_counter | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP07 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.870 | confirm_power_two_sum | linear_term_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP08 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.929 | confirm_symmetric_products | linear_term_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP09 | P2B-TR-LP-SHIFTED_PRODUCT-01 | 0.930 | confirm_descending_sum | shifted_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP10 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.933 | confirm_square_even_sum | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP11 | P2B-TR-LP-EVEN_MINUS_ODD-01 | 0.918 | confirm_alternating_square | even_minus_odd_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP12 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.944 | confirm_divisor_count | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP13 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.977 | confirm_proper_divisor_sum | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP14 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.926 | confirm_cumulative_triangles | linear_term_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP15 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.944 | confirm_residue_two_sum | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-LP16 | P2B-TR-LP-LINEAR_TERM_SUM-01 | 0.906 | confirm_rising_cubic_sum | linear_term_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN02 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.862 | confirm_average_three | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN03 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.977 | confirm_triangle_area | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN05 | P2B-TR-FN-CLAMP_FUNCTION-01 | 0.933 | confirm_bounded_shift | clamp_function_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN06 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.894 | confirm_absolute_pair_sum | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN08 | P2B-TR-FN-CONDITIONAL_FUNCTION-01 | 0.938 | confirm_parity_value | conditional_function_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN09 | P2B-TR-FN-COMPOSED_FUNCTIONS-01 | 0.950 | confirm_two_stage_offset | composed_functions_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN10 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.963 | confirm_rectangle_perimeter | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN12 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.873 | confirm_weighted_three | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN13 | P2B-TR-FN-COMPOSED_FUNCTIONS-01 | 0.975 | confirm_square_then_half | composed_functions_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN14 | P2B-TR-FN-CONDITIONAL_FUNCTION-01 | 0.964 | confirm_threshold_return | conditional_function_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN15 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.979 | confirm_remainder_function | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-FN16 | P2B-TR-FN-WEIGHTED_PAIR-01 | 0.896 | confirm_distance_origin | weighted_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR05 | P2B-TR-AR-COUNT_EVEN_FIVE-01 | 0.966 | confirm_negative_count | count_even_five_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR06 | P2B-TR-AR-COUNT_EVEN_FIVE-01 | 0.952 | confirm_odd_sum | count_even_five_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR09 | P2B-TR-CP-ARRAY_POSITIVE_SUM-01 | 0.860 | confirm_above_average_count | array_positive_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR11 | P2B-TR-CP-ARRAY_POSITIVE_SUM-01 | 0.936 | confirm_square_sum | array_positive_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR12 | P2B-TR-AR-COUNT_EVEN_FIVE-01 | 0.965 | confirm_zero_count | count_even_five_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR15 | P2B-TR-AR-COUNT_EVEN_FIVE-01 | 0.931 | confirm_bounded_sum | count_even_five_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-AR16 | P2B-TR-CP-ARRAY_POSITIVE_SUM-01 | 0.914 | confirm_weighted_positions | array_positive_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-ST03 | P2B-TR-ST-REPLACE_VOWEL-01 | 0.886 | confirm_dual_replace | replace_vowel_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-ST07 | P2B-TR-CP-STRING_LENGTH_CLASS-01 | 0.963 | confirm_starts_pre | string_length_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-ST08 | P2B-TR-CP-STRING_LENGTH_CLASS-01 | 0.963 | confirm_ends_ing | string_length_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-ST14 | P2B-TR-ST-CONTAINS_LABEL-01 | 0.957 | confirm_palindrome | contains_label_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-ST16 | P2B-TR-ST-CONTAINS_LABEL-01 | 0.876 | confirm_case_swap_proxy | contains_label_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO01 | P2B-TR-IO-LENGTH_PRODUCT-01 | 0.920 | confirm_numeric_triple_tag | length_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO03 | P2B-TR-IO-CASE_PAIR-01 | 0.960 | confirm_lower_upper_tilde | case_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO04 | P2B-TR-IO-CASE_PAIR-01 | 0.960 | confirm_double_reverse | case_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO07 | P2B-TR-IO-TWO_LABELED_LINES-01 | 0.856 | confirm_repeat_plus_one | two_labeled_lines_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO08 | P2B-TR-IO-TAGGED_PAIR-01 | 0.962 | confirm_decrement_with_unit | tagged_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO10 | P2B-TR-IO-CASE_PAIR-01 | 0.960 | confirm_lower_pipe_upper | case_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO11 | P2B-TR-IO-TWO_LABELED_LINES-01 | 0.922 | confirm_reverse_order_lines | two_labeled_lines_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO12 | P2B-TR-IO-LENGTH_PRODUCT-01 | 0.932 | confirm_combined_length_label | length_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO13 | P2B-TR-IO-LENGTH_PRODUCT-01 | 0.944 | confirm_first_chars | length_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO14 | P2B-TR-IO-CASE_PAIR-01 | 0.937 | confirm_last_chars | case_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO15 | P2B-TR-IO-LENGTH_PRODUCT-01 | 0.932 | confirm_numeric_sum_label | length_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-IO16 | P2B-TR-IO-TAGGED_PAIR-01 | 0.966 | confirm_repeat_separator | tagged_pair_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP01 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.918 | confirm_proper_divisor_class | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP02 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.922 | confirm_prime_proxy | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP03 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.962 | confirm_square_sum_parity | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP04 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.933 | confirm_filtered_square_sum | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP05 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.913 | confirm_divisor_parity | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP07 | P2B-TR-LP-NONMULTIPLE_COUNT-01 | 0.930 | confirm_odd_cube_sum | nonmultiple_count_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP08 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.918 | confirm_multiple_difference | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP09 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.935 | confirm_even_product_class | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP11 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.946 | confirm_polynomial_sum_parity | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP12 | P2B-TR-CP-FACTORIAL_CLASS-01 | 0.879 | confirm_alternating_threshold | factorial_class_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP13 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.896 | confirm_count_two_or_five | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP14 | P2B-TR-LP-SHIFTED_PRODUCT-01 | 0.935 | confirm_remainder_accumulation | shifted_product_1 | retain: distinct semantics; shared scaffold |
| P2B-EVAL-CP15 | P2B-TR-CP-INCLUDE_EXCLUDE_SUM-01 | 0.863 | confirm_nested_small_products | include_exclude_sum_1 | retain: distinct semantics; shared scaffold |

## Exact AST-proxy flags reviewed

| evaluation | training | AST proxy | evaluation operation | training operation | resolution |
|---|---|---|---|---|---|
| P2B-EVAL-EV06 | P2B-TR-ST-COUNT_LETTER-05 | IMPORT>INPUT>DISPLAYNL>+ | sqrt_shift | substring_count | retain: proxy omits called operation |
| P2B-EVAL-LP02 | P2B-TR-LP-NONMULTIPLE_COUNT-05 | INPUT>LOOP><=>+>+>IF>%>!=>+=>DISPLAYNL | odd_counter | loop_filter | retain: proxy omits called operation |
| P2B-EVAL-LP05 | P2B-TR-LP-LINEAR_TERM_SUM-05 | INPUT>LOOP><=>+>+>+=>*>+>DISPLAYNL | bilinear_index_sum | counted_loop | retain: proxy omits called operation |
| P2B-EVAL-ST01 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | labeled_upper_reverse | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST02 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | lower_length | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST03 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | dual_replace | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST05 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | count_go | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST06 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | labeled_trim_reverse | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST07 | P2B-TR-ST-CONTAINS_LABEL-05 | IMPORT>INPUT>IF>DISPLAYNL>ELSE>DISPLAYNL | starts_pre | contains | retain: proxy omits called operation |
| P2B-EVAL-ST08 | P2B-TR-ST-CONTAINS_LABEL-05 | IMPORT>INPUT>IF>DISPLAYNL>ELSE>DISPLAYNL | ends_ing | contains | retain: proxy omits called operation |
| P2B-EVAL-ST09 | P2B-TR-ST-COUNT_LETTER-05 | IMPORT>INPUT>DISPLAYNL>+ | count_a_e | substring_count | retain: proxy omits called operation |
| P2B-EVAL-ST10 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | labeled_repeat_reverse | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST12 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | replace_spaces | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-ST14 | P2B-TR-ST-CONTAINS_LABEL-05 | IMPORT>INPUT>IF>DISPLAYNL>ELSE>DISPLAYNL | palindrome | contains | retain: proxy omits called operation |
| P2B-EVAL-ST16 | P2B-TR-ST-CONTAINS_LABEL-05 | IMPORT>INPUT>IF>DISPLAYNL>ELSE>DISPLAYNL | case_swap_proxy | contains | retain: proxy omits called operation |
| P2B-EVAL-IO03 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | lower_upper_tilde | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-IO04 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | double_reverse | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-IO06 | P2B-TR-IO-TWO_LABELED_LINES-05 | IMPORT>INPUT>DISPLAYNL>DISPLAYNL | lower_labels | two_line_format | retain: proxy omits called operation |
| P2B-EVAL-IO09 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | braced_fields | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-IO10 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | lower_pipe_upper | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-IO11 | P2B-TR-IO-TWO_LABELED_LINES-05 | IMPORT>INPUT>DISPLAYNL>DISPLAYNL | reverse_order_lines | two_line_format | retain: proxy omits called operation |
| P2B-EVAL-IO12 | P2B-TR-ST-COUNT_LETTER-05 | IMPORT>INPUT>DISPLAYNL>+ | combined_length_label | substring_count | retain: proxy omits called operation |
| P2B-EVAL-IO13 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | first_chars | field_reverse | retain: proxy omits called operation |
| P2B-EVAL-IO15 | P2B-TR-ST-COUNT_LETTER-05 | IMPORT>INPUT>DISPLAYNL>+ | numeric_sum_label | substring_count | retain: proxy omits called operation |
| P2B-EVAL-IO16 | P2B-TR-IO-REVERSED_FIELDS-05 | IMPORT>INPUT>DISPLAYNL | repeat_separator | field_reverse | retain: proxy omits called operation |

## Prior consumed-suite normalized-code flags reviewed

| evaluation | nearest consumed task | similarity | resolution |
|---|---|---|---|
| P2B-EVAL-EV01 | P2A-DEV-EV01 | 0.938 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV02 | P2A-DEV-EV05 | 0.966 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV03 | RDEV-EV-002 | 0.967 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV04 | P1T-EV01 | 0.969 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV05 | P2A-DEV-EV03 | 0.980 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV06 | P2A-DEV-EV07 | 0.921 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV07 | P2A-DEV-EV07 | 0.923 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV08 | P1T-EV01 | 0.960 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV10 | RDEV-EV-003 | 0.963 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV11 | P1T-EV02 | 0.901 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV12 | P2A-DEV-EV05 | 0.976 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV13 | P2A-DEV-EV05 | 0.969 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV14 | P2A-TR-EV-DISC-01 | 0.975 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-EV15 | P1T-EV05 | 0.963 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD01 | RDEV-CD-002 | 0.965 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD02 | P2A-TR-CD-SIGN-02 | 0.970 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD07 | P1T-CD02 | 0.949 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD08 | RDEV-CD-001 | 0.914 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD09 | P2A-DEV-CD08 | 0.964 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD11 | P1T-CD02 | 0.962 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD12 | P2A-TR-CD-RANGE-01 | 0.920 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD13 | P2A-TR-CD-MAX-01 | 0.914 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD14 | P2A-TR-CD-MAX-01 | 0.922 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CD15 | P2A-TR-CD-RANGE-01 | 0.920 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP01 | P2A-DEV-LP01 | 0.940 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP02 | P2A-DEV-LP02 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP03 | P2A-DEV-LP03 | 0.943 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP04 | P2A-DEV-LP02 | 0.944 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP05 | P2A-DEV-LP05 | 0.947 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP06 | SYN-MOD-LP3-001 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP07 | P2A-DEV-LP07 | 0.960 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP08 | P2A-DEV-LP08 | 0.947 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP09 | P2A-TR-LP-SUM-01 | 0.943 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP10 | SYN-MOD-LP3-001 | 0.941 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP11 | P1T-LP08 | 0.932 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP12 | SYN-MOD-LP3-001 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP13 | SYN-MOD-LP3-001 | 0.915 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP14 | P2A-DEV-LP05 | 0.935 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP15 | SYN-MOD-LP3-001 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-LP16 | P2A-DEV-LP05 | 0.915 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN01 | RDEV-FN-001 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN02 | P2A-DEV-FN02 | 0.936 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN03 | P2A-DEV-FN03 | 0.956 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN04 | P2A-DEV-FN06 | 0.933 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN06 | RDEV-FN-002 | 0.906 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN07 | RDEV-FN-001 | 0.966 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN08 | P2A-DEV-FN07 | 0.952 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN10 | P2A-DEV-FN03 | 0.938 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN12 | P2A-DEV-FN02 | 0.919 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN14 | P2A-DEV-FN07 | 0.963 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN15 | P2A-DEV-FN03 | 0.953 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-FN16 | RDEV-FN-002 | 0.908 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST01 | P1T-ST01 | 0.919 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST03 | P2A-DEV-ST01 | 0.976 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST05 | P1T-ST01 | 0.958 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST06 | RDEV-ST-003 | 0.914 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST07 | P1T-ST07 | 0.913 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST08 | P1T-ST07 | 0.913 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST10 | P1T-ST01 | 0.903 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST12 | P1T-ST04 | 0.911 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-ST14 | P2A-DEV-ST03 | 0.958 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO01 | P2A-DEV-IO04 | 0.970 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO03 | P2A-TR-IO-SLASH-01 | 0.959 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO04 | P2A-TR-IO-SLASH-01 | 0.959 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO07 | P2A-DEV-IO07 | 0.902 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO08 | P2A-TR-IO-SLASH-01 | 0.964 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO10 | P2A-TR-IO-SLASH-01 | 0.959 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO11 | P2A-TR-IO-TWOLINE-01 | 0.956 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO12 | P2A-DEV-IO03 | 0.931 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO13 | P2A-DEV-IO03 | 0.954 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO14 | P2A-DEV-IO04 | 0.947 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO15 | P2A-DEV-IO03 | 0.931 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-IO16 | P2A-TR-IO-SWAP-01 | 0.967 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP01 | P2A-DEV-CP07 | 0.942 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP02 | P2A-DEV-CP07 | 0.945 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP03 | P2A-DEV-CP04 | 0.951 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP04 | SYN-MOD-LP3-001 | 0.941 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP05 | P2A-DEV-CP07 | 0.954 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP07 | P2A-DEV-CP08 | 0.935 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP09 | P2A-DEV-CP07 | 0.933 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP11 | P2A-DEV-CP01 | 0.944 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP12 | P2A-DEV-CP07 | 0.901 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP13 | P2A-DEV-CP03 | 0.932 | retain: below 0.98; prompt/semantic task differs |
| P2B-EVAL-CP14 | P2A-TR-LP-SUM-01 | 0.948 | retain: below 0.98; prompt/semantic task differs |

## Reviewer conclusion

All listed pairs were reviewed against task prompts, reference programs, algorithm labels, lineages, structural signatures, and semantic-operation labels. The four prompt flags express broad family-level wording rather than the same mapping. The 81 train/evaluation code flags and 25 exact AST proxies reflect mandatory GOCO declarations, pipe-splitting boilerplate, loop shells, or one-call string skeletons; none is a renamed or literal-only copy. The 84 prior-suite code flags are all below 0.98 after the final replacements, and there are zero prior prompt flags at 0.70. The suite is therefore accepted for preregistration with distance bucket retained as a task-level analysis factor.
