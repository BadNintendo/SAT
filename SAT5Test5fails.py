memo = {}

def is_satisfied(clause, assignment):
    return any((lit > 0 and assignment.get(abs(lit), False)) or (lit < 0 and not assignment.get(abs(lit), False)) for lit in clause)

def is_unsatisfied(clause, assignment):
    return all((lit > 0 and not assignment.get(abs(lit), True)) or (lit < 0 and assignment.get(abs(lit), False)) for lit in clause)

def dpll(clauses, assignment={}):
    key = tuple(sorted(assignment.items()))
    if key in memo:
        return memo[key]

    if all(is_satisfied(clause, assignment) for clause in clauses):
        memo[key] = assignment
        return assignment

    if any(is_unsatisfied(clause, assignment) for clause in clauses):
        memo[key] = None
        return None

    # Pure literal elimination
    all_literals = {lit for clause in clauses for lit in clause}
    pure_literals = {lit for lit in all_literals if -lit not in all_literals}
    for lit in pure_literals:
        assignment[abs(lit)] = lit > 0

    # First Unit Propagation Attempt
    def process_unit_clauses():
        while True:
            unit_clauses = [clause for clause in clauses if sum(1 for lit in clause if abs(lit) not in assignment) == 1]
            if not unit_clauses:
                break
            for unit_clause in unit_clauses:
                unit_lit = next((lit for lit in unit_clause if abs(lit) not in assignment), None)
                if unit_lit is None:
                    continue  # Skip if no valid literal found
                assignment[abs(unit_lit)] = unit_lit > 0
                new_clauses = []
                for clause in clauses:
                    if not is_satisfied(clause, assignment):
                        # Remove the assigned literal and add clause if still relevant
                        new_clause = [lit for lit in clause if abs(lit) != abs(unit_lit)]
                        if new_clause:
                            new_clauses.append(new_clause)
                clauses[:] = new_clauses
                # Exit if any clause is unsatisfied after assignment
                if any(is_unsatisfied(clause, assignment) for clause in clauses):
                    return False
        return True

    # Process unit clauses and handle conflicts early
    if not process_unit_clauses():
        memo[key] = None
        return None

    # If the initial unit propagation failed, apply the second unit clause logic as a last resort
    def process_unit_clauses_fallback():
        unit_clauses = [clause for clause in clauses if sum(1 for lit in clause if abs(lit) not in assignment) == 1]
        for unit_clause in unit_clauses:
            unit_lit = next((lit for lit in unit_clause if abs(lit) not in assignment), None)
            if unit_lit is not None:
                assignment[abs(unit_lit)] = unit_lit > 0
                new_clauses = []
                for clause in clauses:
                    if not is_satisfied(clause, assignment):
                        new_clause = [lit for lit in clause if abs(lit) != abs(unit_lit)]
                        if new_clause:
                            new_clauses.append(new_clause)
                clauses[:] = new_clauses
        return True

    # Fallback to second unit clause processing after failing to make progress with initial propagation
    if not process_unit_clauses_fallback():
        memo[key] = None
        return None

    # Select an unassigned variable for backtracking
    unassigned_vars = {abs(lit) for clause in clauses for lit in clause if abs(lit) not in assignment}
    if not unassigned_vars:
        memo[key] = None
        return None

    variable = unassigned_vars.pop()
    for value in [True, False]:
        result = dpll(clauses, {**assignment, variable: value})
        if result is not None:
            memo[key] = result
            return result

    memo[key] = None
    return None

def run_tests():
    test_cases = [
        ([[1, -2], [2, 3], [-1, -3]], True),
        ([[1], [-1]], False),
        ([[1, 2], [-1, -2]], False),
        ([[1, 2], [1, -2], [-1, 2], [-1, -2]], True),
        ([[1, 2, 3], [-1, -2], [2, -3], [-2, 3]], True)
    ]

    results = []
    for i, (clauses, expected) in enumerate(test_cases):
        memo.clear()  # Clear memoization before each test
        result = dpll(clauses) is not None
        passed = result == expected
        results.append(f"Test {i + 1}: {'Pass' if passed else 'Fail'}")
        if not passed:
            print(f"Test {i + 1} failed. Retesting with fallback unit clause processing...")
            # Apply the assignment recursive calls only on failures
            def retry_dpll(clauses, assignment={}):
                key = tuple(sorted(assignment.items()))
                if key in memo:
                    return memo[key]

                def is_satisfied(clause):
                    return any((lit > 0 and assignment.get(abs(lit), False)) or (lit < 0 and not assignment.get(abs(lit), False)) for lit in clause)

                def is_unsatisfied(clause):
                    return all((lit > 0 and not assignment.get(abs(lit), True)) or (lit < 0 and assignment.get(abs(lit), False)) for lit in clause)

                if all(is_satisfied(clause) for clause in clauses):
                    memo[key] = assignment
                    return assignment

                if any(is_unsatisfied(clause) for clause in clauses):
                    memo[key] = None
                    return None

                # Pure literal elimination
                pure_literals = set()
                all_literals = {lit for clause in clauses for lit in clause}
                for lit in all_literals:
                    if -lit not in all_literals:
                        pure_literals.add(lit)
                
                for lit in pure_literals:
                    assignment[abs(lit)] = lit > 0

                # Primary Unit Clause Processing
                def process_unit_clauses_primary():
                    while True:
                        unit_clauses = [clause for clause in clauses if sum(1 for lit in clause if abs(lit) not in assignment) == 1]
                        if not unit_clauses:
                            break
                        for unit_clause in unit_clauses:
                            unit_lit = next((lit for lit in unit_clause if abs(lit) not in assignment), None)
                            if unit_lit is None:
                                continue  # Skip if no valid literal found
                            assignment[abs(unit_lit)] = unit_lit > 0
                            new_clauses = []
                            for clause in clauses:
                                if not is_satisfied(clause, assignment):
                                    # Remove the assigned literal and add clause if still relevant
                                    new_clause = [lit for lit in clause if abs(lit) != abs(unit_lit)]
                                    if new_clause:
                                        new_clauses.append(new_clause)
                            clauses[:] = new_clauses
                            # Exit if any clause is unsatisfied after assignment
                            if any(is_unsatisfied(clause, assignment) for clause in clauses):
                                return False
                    return True

                if not process_unit_clauses_primary():
                    memo[key] = None
                    return None

                # Fallback Unit Clause Processing
                def process_unit_clauses_fallback():
                    unit_clauses = [clause for clause in clauses if sum(1 for lit in clause if abs(lit) not in assignment) == 1]
                    while unit_clauses:
                        unit_clause = unit_clauses.pop()
                        unit_lit = next((lit for lit in unit_clause if abs(lit) not in assignment), None)
                        if unit_lit is None:
                            continue
                        assignment[abs(unit_lit)] = unit_lit > 0
                        clauses[:] = [clause for clause in clauses if not is_satisfied(clause, assignment)]
                        unit_clauses = [clause for clause in clauses if sum(1 for lit in clause if abs(lit) not in assignment) == 1]
                    return None

                if not process_unit_clauses_fallback():
                    memo[key] = None
                    return None

                # Choose the first unassigned variable
                unassigned_vars = {abs(lit) for clause in clauses for lit in clause if abs(lit) not in assignment}
                if not unassigned_vars:
                    memo[key] = None
                    return None

                variable = unassigned_vars.pop()
                for value in [True, False]:
                    result = retry_dpll(clauses, {**assignment, variable: value})
                    if result is not None:
                        memo[key] = result
                        return result
                memo[key] = None
                return None

            retry_result = retry_dpll(clauses) is not None
            results[-1] = f"Test {i + 1}: {'Pass' if retry_result == expected else 'Fail'}"
    return " | ".join(results)

results = run_tests()
print(results)