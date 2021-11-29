from parse import read_input_file, write_output_file
import os, random

p = 0.9
def greedy(tasks, time):
    if not tasks:
        return [], 0
    best_duration = 0
    best_ratio = 0
    best_task = None
    best_benefit = 0
    for task in tasks[:]:
        duration = task.get_duration()
        if time + duration > 1440:
            tasks.remove(task)
            continue
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
        return [], 0
    task_list, profit = greedy([x for x in tasks if x != best_task], time + best_duration)
    # p pick best and go with it
    # 1-p pick best and random and find best of two
    random_float = random.random()
    if (random_float > p):
        rand_task = tasks[random.randint(0, len(tasks) - 1)]
        rand_task_list, rand_profit = greedy([x for x in tasks if x != rand_task], time + rand_task.get_duration())
        total_rand_profit = rand_profit + rand_task.get_late_benefit(time - rand_task.get_deadline())
        if (total_rand_profit > profit + best_benefit):
            return [rand_task.get_task_id()] + rand_task_list, total_rand_profit
    return [best_task.get_task_id()] + task_list, profit + best_benefit

def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
    output, profit = greedy(tasks, 0)
    print(profit)
    return output
        
if __name__ == '__main__':
    for input_path in os.listdir('inputs/'):
        if input_path[0] == ".":
            continue
        output_path = 'outputs/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs/' + input_path)
        output = solve(tasks)
        write_output_file(output_path, output)
