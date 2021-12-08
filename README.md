# CS 170 Project Fall 2021

Take a look at the project spec before you get started!

Requirements:

Python 3.6+

Files:
- `parse.py`: functions to read/write inputs and outputs
- `solver.py`: where you should be writing your code to solve inputs
- `Task.py`: contains a class that is useful for processing inputs

When writing inputs/outputs:
- Make sure you use the functions `write_input_file` and `write_output_file` provided
- Run the functions `read_input_file` and `read_output_file` to validate your files before submitting!
- These are the functions run by the autograder to validate submissions

To generate outputs, simply run python3 solver.py. You can change whether you want to generate the small, medium, or large outputs by going to the end of the solver.py file where main is and changing the input/output paths.
For example, if you wanted the medium outputs, there are 2 parts that you have to change to 'inputs/medium/' and one part to change to 'outputs/medium/'