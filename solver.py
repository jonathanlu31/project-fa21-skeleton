from parse import read_input_file, write_output_file
import os, random, math, heapq, numpy as np

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
    best_weight = float("-inf")
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
        ratio = benefit / duration
        # regret = get_regret(time, task, tasks)
        weight = benefit * 0.41 - duration * 0.58 - deadline * 0.01
        if weight > best_weight:
            best_task_index = i
            best_weight = weight
    if best_task_index == -1:
        return [], 0, tasks
    best_task = tasks[best_task_index]
    task_list, profit, remaining = greedy_weighted([task for task in viable_tasks if task != best_task], time + best_task.get_duration())
    profit += best_task.get_late_benefit(time + best_task.get_duration() - best_task.get_deadline())
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if random_float > p:
        rand_task = viable_tasks[random.randint(0, len(viable_tasks) - 1)]
        rand_task_list, rand_profit, rand_remaining = greedy_weighted([x for x in viable_tasks if x != rand_task], time + rand_task.get_duration())
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
    regret = -float("inf")
    for task in remaining:
        if task == curr_task:
            continue
        regret_duration = time + duration + task.get_duration()
        if regret_duration > task.get_deadline():
            regret = max(regret, task.get_late_benefit(regret_duration - task.get_deadline()) - task.get_late_benefit(time+task.get_duration()-task.get_deadline()))
    return regret - curr_task.get_late_benefit(time + duration - curr_task.get_deadline())

def get_weight(task, task_dur, time, regret):
    benefit = task.get_late_benefit(time + task_dur - task.get_deadline())
    # do we need ratio if duration and benefit in weight calc already?
    # ratio = benefit / task_dur
    return benefit * 0.6 - task_dur * 0.2 - regret * 0.2

# def local_search(initial_tasks, soln, remaining):
#     if not remaining:
#         return soln, 0
#     for i in range(0, len(soln) - 1, 2):
#         for _ in range(50):
#             task, timestep = soln[i]
#             task2, timestep2 = soln[i+1]
#             rand_index = random.randint(0, len(remaining) - 1)
#             local_swap = remaining[rand_index]
#             local_end = timestep + local_swap.get_duration()
#             if local_end > timestep2 + task2.get_duration():
#                 continue
#             local_benefit = local_swap.get_late_benefit(local_end - local_swap.get_deadline())
#             og_benefit = task.get_late_benefit(timestep + task.get_duration() - task.get_deadline()) + task2.get_late_benefit(timestep2 + task2.get_duration() - task2.get_deadline())
#             if local_benefit > og_benefit:
#                 soln.pop(i)
#                 soln.pop(i)
#                 soln.insert(i, (local_swap, timestep))
#                 remaining[rand_index] = task
#                 remaining.append(task2)
#                 local_opt, profit_increase = local_search(initial_tasks, soln, remaining)
#                 return local_opt, profit_increase + local_benefit - og_benefit
#     return soln, 0
    
# def local_search_og(soln, remaining):
#     if not remaining:
#         return soln, 0
#     for i in range(len(soln)):
#         for _ in range(50):
#             task, timestep = soln[i]
#             rand_index = random.randint(0, len(remaining) - 1)
#             local_swap = remaining[rand_index]
#             if local_swap.get_duration() > task.get_duration():
#                 continue
#             local_benefit = local_swap.get_late_benefit(timestep - local_swap.get_deadline())
#             og_benefit = task.get_late_benefit(timestep - task.get_deadline())
#             if local_benefit > og_benefit:
#                 soln[i] = (local_swap, timestep)
#                 remaining[rand_index] = task
#                 local_opt, profit_increase = local_search_og(soln, remaining)
#                 return local_opt, profit_increase + local_benefit - og_benefit
#     return soln, 0

def calc_prof(soln):
    total = 0.0
    time = 0
    for task in soln:
        time += task.get_duration()
        if time > 1440:
            break
        total += task.get_late_benefit(time - task.get_deadline())
    return total

def local_search_swaps(initial_tasks, soln, profit):
    temp = 2000
    alpha = 0.9
    curr_soln = soln
    curr_profit = profit
    while temp > 5:
        for _ in range(50):
            i = random.randint(0, len(curr_soln) - 1)
            task, _ = curr_soln[i]
            soln_cpy = curr_soln[:]
            rand_index = random.randint(0, len(initial_tasks) - 1)
            local_swap = initial_tasks[rand_index]
            if local_swap == task:
                continue
            local_index = -1
            # can add remaining tasks to task_list so you dont have to find the index
            for i in range(len(curr_soln)):
                if curr_soln[i][0].get_task_id() == local_swap.get_task_id():
                    local_index = i
                    break
            if local_index == -1:
                soln_cpy[i] = (local_swap, 0)
            else:
                soln_cpy[local_index] = (task, 0)
                soln_cpy[i] = (local_swap, 0)
            new_profit = calc_prof(soln_cpy)
            difference = new_profit - curr_profit
            if difference > 0:
                curr_soln = soln_cpy
                curr_profit = new_profit
            else:
                # replace with prob e^(delta/T)
                rand_float = random.random()
                if rand_float < math.exp(difference / temp):
                    curr_soln = soln_cpy
                    curr_profit = new_profit
        temp *= alpha
    return curr_soln, calc_prof(curr_soln)

def genetic(tasks):
    """
    init: generate 500 random answers
    take the top ten for next gen
    crossover: select 2 parents, choose a random point to splice at and swap the sequence
    mutation: for every igloo of the child, mutate with small probability to something random
    repeat for x iterations
    return the best one
    hyperparameters: popsize, crossover rate, mutation rate, end condition, parent selection algorithm
    """
    pop_size = 500
    population = init_pop(pop_size, tasks)
    for _ in range(100):
        prof_list = [(x, calc_prof(x)) for x in population]
        top_ten = heapq.nlargest(10, prof_list, key=lambda x: x[1])
        next_gen = [x[0] for x in top_ten]
        for _ in range(0, 490, 2):
            p1, p2 = select_parents(prof_list, pop_size)
            c1, c2 = crossover(p1, p2)
            mutate(c1, tasks)
            mutate(c2, tasks)
            next_gen.append(c1)
            next_gen.append(c2)
        population = next_gen
    return max_prof_instance(population)

def init_pop(pop_size, tasks):
    pop = []
    for _ in range(pop_size):
        pop.append(gen_rand_task_list(tasks))
    return pop

def gen_rand_task_list(tasks):
    time = 0
    task_permutation = np.random.permutation(len(tasks))
    task_list = []
    for task_index in task_permutation:
        selected_task = tasks[task_index]
        if time + selected_task.get_duration() <= 1440:
            task_list.append(selected_task)
            time += selected_task.get_duration()
        if time >= 1440:
            break
    return task_list

def select_parents(prof_list, pop_size):
    parents = []
    for _ in range(2):
        p_candidate1 = prof_list[random.randint(0, pop_size - 1)]
        p_candidate2 = prof_list[random.randint(0, pop_size - 1)]
        # parents.append(max(p_candidate1, p_candidate2, key=lambda x: prof_list[x][1]))
        if p_candidate1[1] > p_candidate2[1]:
            parents.append(p_candidate1[0])
        else:
            parents.append(p_candidate2[0])
    return parents

def crossover(p1, p2):
    rand_ind = random.randint(0, min(len(p1), len(p2)) - 1)
    p1_left, p1_right = p1[:rand_ind], p1[rand_ind:]
    p2_left, p2_right = p2[:rand_ind], p2[rand_ind:]
    child1 = p1_left + p2_right
    child2 = p2_left + p1_right
    return child1, child2

def mutate(soln, tasks):
    p = 0.01
    for i in range(len(soln)):
        random_float = random.random()
        if random_float < p:
            rand_ind = random.randint(0, len(tasks) - 1)
            i = random.randint(0, len(soln) - 1)
            soln_task = soln[i]
            swap_task = tasks[rand_ind]
            if soln_task is swap_task:
                continue
            local_index = -1
            for i in range(len(soln)):
                if soln[i].get_task_id() == swap_task.get_task_id():
                    local_index = i
                    break
            if local_index == -1:
                soln[i] = swap_task
            else:
                soln[local_index] = soln_task
                soln[i] = swap_task

def max_prof_instance(pop):
    max_prof_inst = None
    max_profit = 0
    for instance in pop:
        profit = calc_prof(instance)
        if profit > max_profit:
            max_profit = profit
            max_prof_inst = instance
    return max_prof_inst, max_profit


def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
    # output, profit, remaining = greedy_weighted(tasks, 0)
    # new_output, new_profit = local_search_swaps(tasks, output, profit)
    # print(new_profit, new_profit - profit)
    output, profit = genetic(tasks)
    print(profit)
    return [task.get_task_id() for task in output], profit
        
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
