// Example clauses in Conjunctive Normal Form (CNF)
const clauses = [
    [1, -3, 4],  // Clause 1: Represents (A OR NOT C OR D)
    [-1, 2],     // Clause 2: Represents (NOT A OR B)
    [-2, 3],     // Clause 3: Represents (NOT B OR C)
    [-4]         // Clause 4: Represents (NOT D)
];

// Global cache (memo) to store known results of partial assignments
const memo = {};

/**
 * DPLL SAT Solver with advanced caching.
 * This function implements the DPLL algorithm to solve SAT problems, using memoization
 * to improve efficiency by caching results of previously computed assignments.
 *
 * @param {Array} clauses - An array of clauses in Conjunctive Normal Form (CNF).
 *                          Each clause is an array of integers, where a positive integer
 *                          represents a variable (e.g., A, B, C) and a negative integer
 *                          represents its negation (e.g., NOT A).
 * @param {Object} assignment - A partial truth assignment for the variables, where the
 *                              keys are variable indices and the values are booleans
 *                              indicating whether the variable is true or false.
 * @returns {Object|null} - Returns a satisfying assignment (object) if SAT, or null if UNSAT.
 */
const dpll = (clauses, assignment = {}) => {
    // Convert the current assignment to a JSON string for use as a unique cache key
    const key = JSON.stringify(assignment);

    // Check if this partial assignment has already been computed; return cached result if so
    if (memo[key] !== undefined) {
        return memo[key]; // Early return of cached result for efficiency
    }

    // Base case: Check if all clauses are satisfied by the current assignment
    if (clauses.every(clause => clause.some(lit => assignment[Math.abs(lit)] === (lit > 0)))) {
        memo[key] = assignment; // Cache the satisfying assignment
        return assignment;
    }

    // Base case: Check if any clause is unsatisfiable (all literals are false)
    if (clauses.some(clause => clause.every(lit => assignment[Math.abs(lit)] === (lit < 0)))) {
        memo[key] = null; // Cache this result as unsatisfiable
        return null;
    }

    // Unit propagation: Identify unit clauses and assign their literals
    const unitClause = clauses.find(clause => clause.filter(lit => assignment[Math.abs(lit)] === undefined).length === 1);
    if (unitClause) {
        const unitLit = unitClause.find(lit => assignment[Math.abs(lit)] === undefined);
        return dpll(clauses, { ...assignment, [Math.abs(unitLit)]: unitLit > 0 }); // Recursive call with updated assignment
    }

    // Select an unassigned variable for branching (simple heuristic)
    const [variable] = clauses.flat().map(Math.abs).filter(v => assignment[v] === undefined);

    // Recursively attempt to assign the variable as true, then as false
    const result = dpll(clauses, { ...assignment, [variable]: true }) ||
                   dpll(clauses, { ...assignment, [variable]: false });

    // Cache the result for this assignment to optimize future queries
    memo[key] = result; // Store result for the current assignment
    return result; // Return the computed result
};

// Execute the SAT solver and log the output
const result = dpll(clauses);
console.log(result ? "SATISFIABLE with assignment: " + JSON.stringify(result) : "UNSATISFIABLE");

/*
    Explanation for Developers:
    - This enhanced implementation of the DPLL algorithm leverages a global cache (`memo`) to store results of previous and partial assignments.
    - The cache is accessed and updated using a unique key generated from the current assignment, allowing for rapid retrieval of results for previously computed states.
    - By checking the cache before proceeding with the computation, the algorithm minimizes CPU usage and improves performance, particularly in scenarios with overlapping clauses.

    Benefits:
    - The caching mechanism allows for quick returns of results for previously processed assignments, significantly enhancing performance for large datasets where a considerable portion of clauses may overlap with earlier computations.
    - This approach effectively prevents unnecessary calculations for parts of the problem that have already been resolved, thereby streamlining the resolution of SAT problems.

    Considerations:
    - With increasing cache size due to larger datasets, careful memory management strategies may need to be implemented to avoid excessive memory usage.
    - Developers may want to introduce cache eviction policies or limits on cache size, ensuring that the caching mechanism remains efficient without consuming excessive resources.
    - The design of the caching mechanism should be tailored to the specific requirements of the application, balancing performance improvements against memory overhead.
*/
