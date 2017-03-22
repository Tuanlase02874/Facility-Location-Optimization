# --------------------------------------------------------------------------
# Source file provided under Apache License, Version 2.0, January 2004,
# http://www.apache.org/licenses/
# (c) Copyright IBM Corp. 2015, 2016
# --------------------------------------------------------------------------

from collections import namedtuple
import json

from docplex.util.environment import get_environment
from docplex.mp.absmodel import AbstractModel

# ------------------------------

DEFAULT_ROLL_WIDTH = 110
DEFAULT_ITEMS = [(1, 20, 48), (2, 45, 35), (3, 50, 24), (4, 55, 10), (5, 75, 8)]
DEFAULT_PATTERNS = [(i, 1) for i in range(1, 6)]  # (1, 1), (2, 1) etc
DEFAULT_PATTERN_ITEM_FILLED = [(p, p, 1) for p in range(1, 6)]  # pattern1 for item1, pattern2 for item2, etc.

FIRST_GENERATION_DUALS = [1, 1, 1, 1, 0]


class TItem(object):
    def __init__(self, item_id, item_size, demand):
        self.id = item_id
        self.size = item_size
        self.demand = demand
        self.dual_value = -1

    @classmethod
    def make(cls, args):
        arg_id = args[0]
        arg_size = args[1]
        arg_demand = args[2]
        return cls(arg_id, arg_size, arg_demand)

    def __str__(self):
        return 'item%d' % self.id


class TPattern(namedtuple("TPattern", ["id", "cost"])):

    def __str__(self):
        return 'pattern%d' % self.id


class CuttingStockPatternGeneratorModel(AbstractModel):
    """ The cutting stock pattern-generation model."""

    def __init__(self, master_items, roll_width, **kwargs):
        AbstractModel.__init__(self, 'CuttingStock_PatternGeneratorModel', **kwargs)
        self.items = master_items
        # default values
        self.duals = [1] * len(master_items)
        self.use_vars = {}
        self.roll_width = roll_width

    def setup_variables(self):
        self.use_vars = self.integer_var_list(self.items, ub=999999, name='Use')

    def load_data(self, *args):
        self.items = [TItem.make(it_row) for it_row in args[0]]
        self.duals = args[1][:]
        self.roll_width = args[2]

    def update_duals(self, new_duals):
        """ Update the duals array"""
        self.duals = new_duals
        # duals not used in constraint , only objective has to be updated
        self.setup_objective()

    def clear(self):
        self.use_vars = {}
        AbstractModel.clear(self)

    def setup_constraints(self):
        self.add_constraint(self.scal_prod(self.use_vars, (it.size for it in self.items)) <= self.roll_width)

    def setup_objective(self):
        """ NOTE: this method is called at each loop"""
        self.minimize(1 - self.scal_prod(self.use_vars, self.duals))

    def get_use_values(self):
        assert self.solution

        return [use_var.solution_value for use_var in self.use_vars]


class FirstPatternGeneratorModel(CuttingStockPatternGeneratorModel):
    """ a specialized generator model to check the first iteration of pattern generation."""

    def __init__(self):
        CuttingStockPatternGeneratorModel.__init__(self, DEFAULT_ITEMS, DEFAULT_ROLL_WIDTH)
        self.update_duals(FIRST_GENERATION_DUALS)


class CutStockMasterModel(AbstractModel):
    """ The cutting stock master model. """

    def __init__(self, **kwargs):
        AbstractModel.__init__(self, 'Cutting Stock Master', **kwargs)
        self.items = []
        self.patterns = []
        self.pattern_item_filled = {}

        self.max_pattern_id = -1
        self.items_by_id = {}
        self.patterns_by_id = {}
        # results
        self.best_cost = -1
        self.nb_iters = -1
        self.item_fill_cts = []
        self.cut_vars = {}

        self.roll_width = 99999
        self.MAX_CUT = 9999

    def clear(self):
        AbstractModel.clear(self)
        self.item_fill_cts = []
        self.cut_vars = {}

    def load_data(self, item_table, pattern_table, fill_table, roll_width):
        self.items = [TItem.make(it_row) for it_row in item_table]
        self.items_by_id = {it.id: it for it in self.items}
        self.patterns = [TPattern(*pattern_row) for pattern_row in pattern_table]
        self.patterns_by_id = {pat.id: pat for pat in self.patterns}
        self.max_pattern_id = max(pt.id for pt in self.patterns)

        # build a dictionary storing how much each pattern fills each item.
        self.pattern_item_filled = {(self.patterns_by_id[p], self.items_by_id[i]): f for (p, i, f) in fill_table}
        self.roll_width = roll_width

    def add_new_pattern(self, item_usages):
        """ makes a new pattern from a sequence of usages (one per item)"""
        new_pattern_id = self.max_pattern_id + 1
        new_pattern = TPattern(new_pattern_id, 1)
        self.patterns.append(new_pattern)
        self.max_pattern_id = new_pattern_id
        for used, item in zip(item_usages, self.items):
            self.pattern_item_filled[new_pattern, item] = used

    def setup_variables(self):
        # how much to cut?
        self.cut_vars = self.continuous_var_dict(self.patterns, lb=0, ub=self.MAX_CUT, name='Cut')

    def setup_constraints(self):
        all_items = self.items
        all_patterns = self.patterns

        def pattern_item_filled(pattern, item):
            return self.pattern_item_filled[pattern, item] if (pattern, item) in self.pattern_item_filled else 0

        self.item_fill_cts = []
        for item in all_items:
            item_fill_ct = self.sum(
                self.cut_vars[p] * pattern_item_filled(p, item) for p in all_patterns) >= item.demand
            self.item_fill_cts.append(item_fill_ct)
            self.add_constraint(item_fill_ct, 'ct_fill_{0!s}'.format(item))

    def setup_objective(self):
        total_cutting_cost = self.sum(self.cut_vars[p] * p.cost for p in self.patterns)
        self.add_kpi(total_cutting_cost, 'Total cutting cost')
        self.minimize(total_cutting_cost)

    def print_information(self):
        print('#items={}'.format(len(self.items)))
        print('#patterns={}'.format(len(self.patterns)))
        AbstractModel.print_information(self)

    def print_solution(self):
        print("| Nb of cuts | Pattern   | Pattern's detail (# of item1,..., # of item5) |")
        print("| {} |".format("-" * 70))
        for p in self.patterns:
            if self.cut_vars[p].solution_value >= 1e-3:
                pattern_detail = {b.id: self.pattern_item_filled[(a, b)] for (a, b) in self.pattern_item_filled if
                                  a == p}
                print(
                    "| {:<10g} | {!s:9} | {!s:45} |".format(self.cut_vars[p].solution_value,
                                                            p,
                                                            pattern_detail))
        print("| {} |".format("-" * 70))

    def save_solution_as_json(self, file):
        solution = []
        for p in self.patterns:
            if self.cut_vars[p].solution_value >= 1e-3:
                pattern_detail = {b.id: self.pattern_item_filled[(a, b)] for (a, b) in self.pattern_item_filled if
                                  a == p}
                n = {}
                n['pattern'] = str(p)
                n['cuts']= "%g" % self.cut_vars[p].solution_value
                n['details'] = pattern_detail
                solution.append(n)
        file.write(json.dumps(solution, indent=3).encode('utf-8'))

    def run(self, **kwargs):
        master_model = self
        master_model.ensure_setup()
        gen_model = CuttingStockPatternGeneratorModel(master_items=self.items,
                                                      roll_width=self.roll_width,
                                                      output_level=self.output_level,
                                                      **kwargs
                                                      )
        gen_model.setup()
        rc_eps = 1e-6
        obj_eps = 1e-4
        loop_count = 0
        best = 0
        curr = self.infinity
        status = False
        while loop_count < 100 and abs(best - curr) >= obj_eps:
            print('\n#items={},#patterns={}'.format(len(self.items), len(self.patterns)))
            if loop_count > 0:
                self.refresh_model()
            status = master_model.solve(**kwargs)
            loop_count += 1
            best = curr
            if not status:
                print('{}> master model fails, stop'.format(loop_count))
                break
            else:
                assert master_model.solution
                curr = self.objective_value
                print('{}> new column generation iteration, best={:g}, curr={:g}'.format(loop_count, best, curr))
                duals = self.get_fill_dual_values()
                print('{0}> moving duals from master to sub model: {1}'.format(loop_count, map (lambda x: float('%0.2f' % x), duals)))
                gen_model.update_duals(duals)
                status = gen_model.solve(**kwargs)
                if not status:
                    print('{}> slave model fails, stop'.format(loop_count))
                    break

                rc_cost = gen_model.objective_value
                if rc_cost <= -rc_eps:
                    print('{}> slave model runs with obj={:g}'.format(loop_count, rc_cost))
                else:
                    print('{}> pattern-generator model stops, obj={:g}'.format(loop_count, rc_cost))
                    break

                use_values = gen_model.get_use_values()
                print('{}> add new pattern to master data: {}'.format(loop_count, str(use_values)))
                # make a new pattern with use values
                if not (loop_count < 100 and abs(best - curr) >= obj_eps):
                    print('* terminating: best-curr={:g}'.format(abs(best - curr)))
                    break
                self.add_new_pattern(use_values)

        if status:
            print('Cutting-stock column generation terminates, best={:g}, #loops={}'.format(curr, loop_count))
            self.best_cost = curr
            self.nb_iters = loop_count
        else:
            print("Cutting-stock column generation fails")
        return status

    def get_fill_dual_values(self):
        return self.dual_values(self.item_fill_cts)


class DefaultCutStockMasterModel(CutStockMasterModel):
    def __init__(self, **kwargs):
        CutStockMasterModel.__init__(self, **kwargs)
        self.load_data(DEFAULT_ITEMS, DEFAULT_PATTERNS, DEFAULT_PATTERN_ITEM_FILLED, DEFAULT_ROLL_WIDTH)


if __name__ == '__main__':
    """DOcplexcloud credentials can be specified with url and api_key in the code block below.

    Alternatively, Context.make_default_context() searches the PYTHONPATH for
    the following files:

        * cplex_config.py
        * cplex_config_<hostname>.py
        * docloud_config.py (must only contain context.solver.docloud configuration)

    These files contain the credentials and other properties. For example,
    something similar to::

       context.solver.docloud.url = "https://docloud.service.com/job_manager/rest/v1"
       context.solver.docloud.key = "example api_key"
    """
    url = None
    key = None

    cutstock_model = DefaultCutStockMasterModel()
    
    # Solve the model. If a key has been specified above, the solve
    # will use IBM Decision Optimization on cloud.
    if cutstock_model.run(url=url, key=key):
        cutstock_model.print_solution()
        # Save the solution as "solution.json" program output.
        with get_environment().get_output_stream("solution.json") as fp:
            cutstock_model.save_solution_as_json(fp)
