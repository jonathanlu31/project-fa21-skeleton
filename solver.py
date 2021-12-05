from parse import read_input_file, write_output_file
import os, random

p = 0.95
# profit weight
p_w= 0.9
# duration weight
t_w = 0.05
# deadline weight
d_w = 0.05

def greedy_weighted(tasks, time):
    """[summary]

    Args:
        tasks ([list]): list of available tasks to take
        time ([int]): current timestep

    Returns:
        output [list]: solution
        profit [float]: total profit from tasks
        remaining [list]: remaining tasks not taken
    """
    if not tasks:
        return [], 0, tasks
    best_weight = -float("inf")
    best_task_index = -1
    viable_tasks = []
    for i in range(len(tasks)):
        task = tasks[i]
        duration = task.get_duration()
        end_time = time + duration
        if end_time > 1440:
            continue
        viable_tasks.append(task)
        deadline = task.get_deadline()
        benefit = task.get_late_benefit(end_time - deadline)
        weight = benefit * p_w - duration * t_w - deadline * d_w
        if weight > best_weight:
            best_task_index = i
    if best_task_index == -1:
        return [], 0, tasks
    best_task = tasks[best_task_index]
    task_list, profit, remaining = greedy([task for task in viable_tasks if task != best_task], time + best_task.get_duration())
    profit += best_task.get_late_benefit(time + best_task.get_duration() - best_task.get_deadline())
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if random_float > p:
        rand_task = viable_tasks[random.randint(0, len(viable_tasks) - 1)]
        rand_task_list, rand_profit, rand_remaining = greedy([x for x in viable_tasks if x != rand_task], time + rand_task.get_duration())
        rand_profit += rand_task.get_late_benefit(time  + rand_task.get_duration() - rand_task.get_deadline())
        if rand_profit > profit:
            best_task = rand_task
            task_list = rand_task_list
            profit = rand_profit
            remaining = rand_remaining
    return [(best_task, time)] + task_list, profit, remaining

def greedy(tasks, time):
    if not tasks:
        return [], 0, tasks
    best_duration = 0
    #best_ratio = 0
    #best_regret = 0
    best_weight = 0
    best_task = None
    best_benefit = 0
    viable_tasks = []
    for task in tasks:
        duration = task.get_duration()
        end_time = time + duration
        if end_time > 1440:
            continue
        viable_tasks.append(task)
        benefit = task.get_late_benefit(end_time - task.get_deadline())
<<<<<<< HEAD
        ratio = benefit / duration
        if ratio >= best_ratio:
            if ratio > best_ratio:
                best_ratio = ratio
                best_task = task
                best_duration = duration
                best_benefit = benefit
            else:
                if duration < best_duration:
                    best_task = task
                    best_duration = duration
                    best_benefit = benefit
=======
        regret = get_regret(time, task, tasks)
        weight = get_weight(task, duration, time, regret)
        if weight > best_weight:
            best_weight = weight
            best_task = task
            best_duration = duration
            best_benefit = benefit
        # ratio = benefit / duration
        # if ratio >= best_ratio:
        #     if ratio > best_ratio:
        #         best_ratio = ratio
        #         best_task = task
        #         best_duration = duration
        #         best_benefit = benefit
        #     else:
        #         if duration > best_duration:
        #             best_task = task
        #             best_duration = duration
        #             best_benefit = benefit
>>>>>>> a8b7b63efa5352d313e3951c6fdbee96be3e9552
    if not best_task:
        return [], 0, tasks
    task_list, profit, remaining = greedy([x for x in tasks if x != best_task], time + best_duration)
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if random_float > p:
        rand_task = viable_tasks[random.randint(0, len(viable_tasks) - 1)]
        rand_task_list, rand_profit, rand_remaining = greedy([x for x in tasks if x != rand_task], time + rand_task.get_duration())
        total_rand_profit = rand_profit + rand_task.get_late_benefit(time  + rand_task.get_duration() - rand_task.get_deadline())
        if total_rand_profit > profit + best_benefit:
            return [(rand_task, time)] + rand_task_list, total_rand_profit, rand_remaining
    return [(best_task, time)] + task_list, profit + best_benefit, remaining

def get_regret(time, curr_task, remaining):
    duration = curr_task.get_duration()
    regret = 0
    remains = remaining[:]
    if curr_task in remains:
        remains.remove(curr_task)
    for task in remains:
        regret_duration = time + duration + task.get_duration()
        if regret_duration > task.get_deadline():
            regret = max(regret, task.get_late_benefit(regret_duration - task.get_deadline()) - task.get_late_benefit(time+task.get_duration()-task.get_deadline()))
    return regret - curr_task.get_late_benefit(time + duration - curr_task.get_deadline())

def get_weight(task, task_dur, time, regret):
    benefit = task.get_late_benefit(time + task_dur - task.get_deadline())
    # do we need ratio if duration and benefit in weight calc already?
    # ratio = benefit / task_dur
    weight = benefit * 0.6 - task_dur * 0.2 - regret * 0.2
    return weight

def local_search(initial_tasks, soln, remaining):
    if not remaining:
        return soln, 0
    for i in range(0, len(soln) - 1, 2):
        for _ in range(50):
            task, timestep = soln[i]
            task2, timestep2 = soln[i+1]
            rand_index = random.randint(0, len(remaining) - 1)
            local_swap = remaining[rand_index]
            local_end = timestep + local_swap.get_duration()
            if local_end > timestep2 + task2.get_duration():
                continue
            local_benefit = local_swap.get_late_benefit(local_end - local_swap.get_deadline())
            og_benefit = task.get_late_benefit(timestep + task.get_duration() - task.get_deadline()) + task2.get_late_benefit(timestep2 + task2.get_duration() - task2.get_deadline())
            if local_benefit > og_benefit:
                soln.pop(i)
                soln.pop(i)
                soln.insert(i, (local_swap, timestep))
                remaining[rand_index] = task
                remaining.append(task2)
                local_opt, profit_increase = local_search(initial_tasks, soln, remaining)
                return local_opt, profit_increase + local_benefit - og_benefit
    return soln, 0
    
def local_search_og(soln, remaining):
    if not remaining:
        return soln, 0
    for i in range(len(soln)):
        for _ in range(50):
            task, timestep = soln[i]
            rand_index = random.randint(0, len(remaining) - 1)
            local_swap = remaining[rand_index]
            if local_swap.get_duration() > task.get_duration():
                continue
            local_benefit = local_swap.get_late_benefit(timestep - local_swap.get_deadline())
            og_benefit = task.get_late_benefit(timestep - task.get_deadline())
            if local_benefit > og_benefit:
                soln[i] = (local_swap, timestep)
                remaining[rand_index] = task
                local_opt, profit_increase = local_search_og(soln, remaining)
                return local_opt, profit_increase + local_benefit - og_benefit
    return soln, 0

def calc_prof(soln):
    total = 0.0
    time = 0
    for task, _ in soln:
        time += task.get_duration()
        total += task.get_late_benefit(time - task.get_deadline())
    return total

def local_search_swaps(initial_tasks, soln, profit):
    for i in range(len(soln)):
        for j in range(len(soln)):
            if i == j:
                continue
            soln_cpy = soln[:]
            task, _ = soln[i]
            # rand_index = random.randint(0, len(initial_tasks) - 1)
            local_swap = initial_tasks[j]
            local_index = -1
            for i in range(len(soln)):
                if soln[i][0].get_task_id() == local_swap.get_task_id():
                    local_index = i
                    break
            if local_index == -1:
                soln_cpy[i] = (local_swap, 0)
            else:
                soln_cpy[local_index] = (task, 0)
                soln_cpy[i] = (local_swap, 0)
            new_profit = calc_prof(soln_cpy)
            if new_profit > profit:
                return local_search_swaps(initial_tasks, soln_cpy, new_profit)
    return soln, calc_prof(soln)

def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
<<<<<<< HEAD
    output, profit, remaining = greedy_weighted(tasks, 0)
    new_output, new_profit = local_search_og(output, remaining)
    # print(new_profit, new_profit - profit)
    return [task[0].get_task_id() for task in new_output], profit + new_profit
=======
    # output, profit, remaining = greedy(tasks, 0)
    # new_output, new_profit = local_search_og(output, remaining)
    #print(new_profit, new_profit - profit)
    output, profit, remaining = greedy(tasks, 0)
    new_output, increase = local_search_og(output, remaining)
    print(profit + increase, increase)
    return [task[0].get_task_id() for task in new_output]
>>>>>>> a8b7b63efa5352d313e3951c6fdbee96be3e9552
        
if __name__ == '__main__':
    total = 0
    for input_path in os.listdir('inputs_off/small/'):
        if input_path[0] == '.':
            continue
        output_path = 'outputs/small/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs_off/small/' + input_path)
        output, prof = solve(tasks)
        total += prof
        write_output_file(output_path, output)
    print(total)
