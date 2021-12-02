from parse import read_input_file, write_output_file
import os, random

p = 0.95

def greedy(tasks, time):
    if not tasks:
        return [], 0, tasks
    best_duration = 0
    best_ratio = 0
    best_task = None
    best_benefit = 0
    viable_tasks = []
    for task in tasks:
        duration = task.get_duration()
        if time + duration > 1440:
            continue
        viable_tasks.append(task)
        benefit = task.get_late_benefit(time - task.get_deadline())
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
    if not best_task:
        return [], 0, tasks
    task_list, profit, remaining = greedy([x for x in tasks if x != best_task], time + best_duration)
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if random_float > p:
        rand_task = viable_tasks[random.randint(0, len(viable_tasks) - 1)]
        rand_task_list, rand_profit, rand_remaining = greedy([x for x in tasks if x != rand_task], time + rand_task.get_duration())
        total_rand_profit = rand_profit + rand_task.get_late_benefit(time - rand_task.get_deadline())
        if total_rand_profit > profit + best_benefit:
            return [(rand_task, time)] + rand_task_list, total_rand_profit, rand_remaining
    return [(best_task, time)] + task_list, profit + best_benefit, remaining

def local_search(initial_tasks, soln, remaining):
    if not remaining:
        return soln, 0
    for i in range(0, len(soln) - 1, 2):
        for _ in range(50):
            task, timestep = soln[i]
            task2, timestep2 = soln[i+1]
            rand_index = random.randint(0, len(remaining) - 1)
            local_swap = remaining[rand_index]
            if local_swap.get_duration() > task.get_duration() + task2.get_duration():
                continue
            local_benefit = local_swap.get_late_benefit(timestep - local_swap.get_deadline())
            og_benefit = task.get_late_benefit(timestep - task.get_deadline())
            + task2.get_late_benefit(timestep2 - task2.get_deadline())
            if local_benefit > og_benefit:
                soln.pop(i)
                soln.pop(i)
                soln.insert(i, (local_swap, timestep))
                remaining[rand_index] = task
                remaining.append(task2)
                local_opt, profit_increase = local_search(initial_tasks, soln, remaining)
                return local_opt, profit_increase + local_benefit - og_benefit
    return soln, 0
    

def local_search_og(initial_tasks, soln, remaining):
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
                local_opt, profit_increase = local_search(initial_tasks, soln, remaining)
                return local_opt, profit_increase + local_benefit - og_benefit
    return soln, 0



def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
    output, profit, remaining = greedy(tasks, 0)
    new_output, increase = local_search(tasks, output, remaining)
    print(profit + increase, increase)
    return [task[0].get_task_id() for task in new_output]
        
if __name__ == '__main__':
    for input_path in os.listdir('inputs_off/large/'):
        if input_path[0] == '.':
            continue
        output_path = 'outputs/large/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs_off/large/' + input_path)
        output = solve(tasks)
        write_output_file(output_path, output)
