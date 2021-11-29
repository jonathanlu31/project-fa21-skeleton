from parse import read_input_file, write_output_file
import os

def greedy(tasks, time):
    if not tasks:
        return []
    best_duration = 0
    best_ratio = 0
    best_task = None
    best_benefit = 0
    for task in tasks:
        duration = task.get_duration()
        if time + duration > 1440:
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
        return []
    tasks.remove(best_task)
    task_list, profit = greedy(tasks, time + best_duration)
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
        output_path = 'outputs/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs/' + input_path)
        output = solve(tasks)
        write_output_file(output_path, output)