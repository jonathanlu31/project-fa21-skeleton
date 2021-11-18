from parse import read_input_file, write_output_file
import os

def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing  
    """
    return dp(0, tasks)[0]

def memo(fn):
    """If arguments are in the cache, return the igloo list
    Otherwise, call dp and store the result

    Args:
        time ([type]): [description]
    """
    cache = {}
    def helper(time, tasks_left):
        tuple_task = tuple([time] + tasks_left)
        input = hash(tuple_task)
        if input not in cache:
            result = _, __ = fn(time, tasks_left)
            cache[input] = result
            return result
        return cache[input]
    return helper

@memo
def dp(time, tasks_left):
    """Go through tasks_left, do each task, store it.
    Return the max profit (or series of igloos).

    Args:
        time ([type]): [description]
        tasks_left ([type]): [description]
    """
    task_list = []
    max_task_id = -1
    max_profit = 0
    for task in tasks_left:
        finish_time = time + task.get_duration()
        if finish_time > 1440:
            continue
        minutes_late = finish_time - task.get_deadline()
        new_tasks_left = tasks_left[:]
        new_tasks_left.remove(task)
        lst, prof = dp(finish_time, new_tasks_left)
        profit = task.get_late_benefit(minutes_late) + prof

        if profit > max_profit:
            max_profit = profit
            task_list = lst
            max_task_id = task.get_task_id()
    if max_task_id == -1:
        return [], 0
    return [max_task_id] + task_list, max_profit
        
if __name__ == '__main__':
    for input_path in os.listdir('inputs/'):
        output_path = 'outputs/' + input_path[:-3] + '.out'
        print(input_path)
        tasks = read_input_file('inputs/' + input_path)
        output = solve(tasks)
        write_output_file(output_path, output)