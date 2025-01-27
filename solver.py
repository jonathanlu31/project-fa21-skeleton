from parse import read_input_file, write_output_file
import os, random, math, heapq

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
    pop_size = 100
    population = init_pop(pop_size, tasks)
    cross_prob = 0.9
    # prev_max = 0
    # best = -1
    for _ in range(1000):
        prof_list = [(x, calc_prof(x)) for x in population]
        top_ten = heapq.nlargest(10, prof_list, key=lambda x: x[1])
        # prev_max = best
        # best = top_ten[0][1]
        next_gen = [x[0] for x in top_ten]
        for _ in range(0, 490, 2):
            p1, p2 = select_parents(prof_list, pop_size)
            rand_cross = random.random()
            if rand_cross < cross_prob:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1[:], p2[:]
            # rand_mutate = random.random()
            # if rand_mutate < mutate_prob:
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
        p_candidates = [prof_list[random.randint(0, pop_size - 1)] for _ in range(5)]
        parents.append(max(p_candidates, key=lambda x: x[1])[0])
        # if p_candidate1[1] > p_candidate2[1]:
        #     parents.append(p_candidate1[0])
        # else:
        #     parents.append(p_candidate2[0])
    return parents

def crossover(p1, p2):
    rand_ind = random.randint(0, min(len(p1), len(p2)) - 1)
    p1_left, p1_right = p1[:rand_ind], []
    p1_set = set(p1_left)
    for i in range(rand_ind, len(p2)):
        task = p2[i]
        if task in p1_set:
            if i < len(p1):
                p1_right.append(p1[i])
                p1_set.add(p1[i])
        else:
            p1_right.append(p2[i])
            p1_set.add(p2[i])

    p2_left, p2_right = p2[:rand_ind], []
    p2_set = set(p2_left)
    for i in range(rand_ind, len(p1)):
        task = p1[i]
        if task in p2_set:
            if i < len(p2):
                p2_right.append(p2[i])
                p2_set.add(p2[i])
        else:
            p2_right.append(p1[i])
            p2_set.add(p1[i])
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

def calc_prof(soln):
    total = 0.0
    time = 0
    for i in range(len(soln)):
        task = soln[i]
        time += task.get_duration()
        if time > 1440:
            i -= 1
            break
        total += task.get_late_benefit(time - task.get_deadline())
    return total, i

def asa(initial_tasks, soln, profit):
    curr_soln = soln
    curr_prof = profit
    temp = 0.5
    accept_rate = 0.5
    target_rate = 0.44
    N = 2000
    m0, m1, m2 = .56, 560 ** (-1/.15*N), 440 ** (-1/.35*N)
    for i in range(N):
        for _ in range(20):
            i = random.randint(0, len(curr_soln) - 1)
            task = curr_soln[i]
            soln_cpy = curr_soln[:]
            rand_index = random.randint(0, len(initial_tasks) - 1)
            local_swap = initial_tasks[rand_index]
            if local_swap == task:
                continue
            local_index = -1
            for j in range(len(curr_soln)):
                if curr_soln[j].get_task_id() == local_swap.get_task_id():
                    local_index = j
                    break
            if local_index == -1:
                soln_cpy[i] = local_swap
            else:
                soln_cpy[local_index] = task
                soln_cpy[i] = local_swap
        new_profit, _ = calc_prof(soln_cpy)
        difference = new_profit - curr_prof
        if difference > 0 or random.random() < math.exp(difference / temp):
            curr_soln = soln_cpy
            curr_prof = new_profit
            accept_rate = .998 * accept_rate + .002
        else:
            accept_rate = .998 * accept_rate
        if i <= .15*N:
            m0= m0 * m1
            target_rate = .44 + m0
        elif i > .65*N:
            target_rate = target_rate * m2
        else:
            target_rate = .44
        if accept_rate > target_rate:
            temp *= .999
        else:
            temp /= .999
    return curr_soln, calc_prof(curr_soln)


p = 0.05

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
        return [], 0
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
        weight = benefit * 0.41 - duration * 0.58 - deadline * 0.01
        # ratio = benefit / duration
        # weight = ratio - deadline * 0.001
        # regret = get_regret(time, task, tasks)
        # weight = get_weight(task, duration, time, regret)
        if weight > best_weight:
            best_weight = weight
            best_task_index = i
    if best_task_index == -1:
        return [], 0
    best_task = tasks[best_task_index]
    task_list, profit = greedy_weighted([task for task in viable_tasks if task != best_task], time + best_task.get_duration())
    profit += best_task.get_late_benefit(time + best_task.get_duration() - best_task.get_deadline())
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if random_float < p:
        rand_task = viable_tasks[random.randint(0, len(viable_tasks) - 1)]
        rand_task_list, rand_profit = greedy_weighted([x for x in viable_tasks if x != rand_task], time + rand_task.get_duration())
        rand_profit += rand_task.get_late_benefit(time  + rand_task.get_duration() - rand_task.get_deadline())
        if rand_profit > profit:
            best_task = rand_task
            task_list = rand_task_list
            profit = rand_profit
    return [best_task] + task_list, profit

def local_search_swaps(initial_tasks, soln, profit):
    """
    hyperparameters: alpha (temp decay rate), temp decay schedule, starting temp, iterations per temp
    """
    temp = 4000
    alpha = 0.992
    curr_soln = soln
    curr_profit = profit
    while temp > 0.0001:
        # print(curr_profit, prev_profit)
        for _ in range(100):
            # add extra tasks at end if extra time
            i = random.randint(0, len(curr_soln) - 1)
            task = curr_soln[i]
            soln_cpy = curr_soln[:]
            # neighbor_selection = random.random()
            # if neighbor_selection < (temp / 4000):
            rand_index = random.randint(0, len(initial_tasks) - 1)
            local_swap = initial_tasks[rand_index]
            if local_swap == task:
                continue
            local_index = -1
            # can add remaining tasks to task_list so you dont have to find the index
            for j in range(len(curr_soln)):
                if curr_soln[j].get_task_id() == local_swap.get_task_id():
                    local_index = j
                    break
            # else:
            #     if i + 1 == len(curr_soln):
            #         local_index = i - 1
            #     else:
            #         local_index = i + 1
            #     local_swap = curr_soln[local_index]
            if local_index == -1:
                soln_cpy[i] = local_swap
            else:
                soln_cpy[local_index] = task
                soln_cpy[i] = local_swap
            new_profit, _ = calc_prof(soln_cpy)
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

def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
    output, profit = greedy_weighted(tasks, 0)
    # output = gen_rand_task_list(tasks)
    # output = [(x, 0) for x in output]
    # profit = calc_prof(output)
    new_output, (new_profit, end_index) = local_search_swaps(tasks, output, profit)
    print(new_profit, new_profit - profit)
    # output, profit = genetic(tasks)
    # print(profit)
    final_output = output
    final_profit = profit
    if new_profit > profit:
        final_output = new_output[:end_index + 1]
        final_profit = new_profit
    return [task.get_task_id() for task in final_output], final_profit
        
if __name__ == '__main__':
    total = 0
    for input_path in os.listdir('inputs/large/'):
        if input_path[0] == '.':
            continue
        output_path = 'outputs/large/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs/large/' + input_path)
        output, prof = solve(tasks)
        total += prof
        write_output_file(output_path, output)
    print(total)
