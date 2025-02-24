# class LogicEvaluator:
#     """
#     Evaluates a logic expression against a test results matrix.
#     """

#     def evaluate(self, logic_expr: Dict[str, Any], results_matrix: List[List[bool]]) -> bool:
#         """
#         Evaluate the logic expression against the test results matrix.
#         Args:
#             logic_expr: The logic expression in our JSON format
#             results_matrix: List[List[bool]] where results_matrix[i][j] is
#                           True if test j passed at step i
#         Returns:
#             bool: True if the logic expression is satisfied
#         """
#         if not results_matrix or not logic_expr:
#             return False

#         N = len(results_matrix)      # Number of steps
#         M = len(results_matrix[0])   # Number of tests

#         def evaluate_test(condition: Dict[str, Any]) -> bool:
#             test_id = condition["test_id"] - 1  # Convert to 0-based index
#             if test_id >= M:
#                 return False

#             constraints = condition.get("constraints", {})
#             min_step = constraints.get("min_step", 1) - 1  # Convert to 0-based
#             max_step = constraints.get("max_step", N) - 1  # Convert to 0-based
#             before = [t - 1 for t in constraints.get("before", [])]
#             after = [t - 1 for t in constraints.get("after", [])]

#             # Find the first step where this test passes
#             test_pass_step = next(
#                 (i for i in range(min_step, max_step + 1)
#                  if results_matrix[i][test_id]),
#                 None
#             )
#             if test_pass_step is None:
#                 return False

#             # Check before/after constraints
#             for other_test in before:
#                 other_pass_step = next(
#                     (i for i in range(N) if results_matrix[i][other_test]),
#                     None
#                 )
#                 if other_pass_step is None or test_pass_step >= other_pass_step:
#                     return False

#             for other_test in after:
#                 other_pass_step = next(
#                     (i for i in range(N) if results_matrix[i][other_test]),
#                     None
#                 )
#                 if other_pass_step is None or test_pass_step <= other_pass_step:
#                     return False

#             return True

#         def evaluate_operation(expr: Dict[str, Any]) -> bool:
#             operator = expr["operator"]
#             conditions = expr["conditions"]

#             if operator == "AND":
#                 return all(
#                     evaluate_test(c) if c["type"] == "test"
#                     else evaluate_operation(c)
#                     for c in conditions
#                 )
#             elif operator == "OR":
#                 return any(
#                     evaluate_test(c) if c["type"] == "test"
#                     else evaluate_operation(c)
#                     for c in conditions
#                 )
#             elif operator == "SEQUENCE":
#                 last_pass_step = -1
#                 for condition in conditions:
#                     test_id = condition["test_id"] - 1
#                     pass_step = next(
#                         (i for i in range(last_pass_step + 1, N)
#                          if results_matrix[i][test_id]),
#                         None
#                     )
#                     if pass_step is None:
#                         return False
#                     last_pass_step = pass_step
#                 return True
#             elif operator == "EXISTS":
#                 return any(
#                     all(results_matrix[i][c["test_id"] - 1] for c in conditions)
#                     for i in range(N)
#                 )
#             elif operator == "ALL":
#                 return all(
#                     all(results_matrix[i][c["test_id"] - 1] for c in conditions)
#                     for i in range(N)
#                 )
#             return False

#         return evaluate_operation(logic_expr)
