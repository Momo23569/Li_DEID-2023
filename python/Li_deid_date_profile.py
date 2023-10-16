import re
import sys
import cProfile

"""
The difference between this file and the Li_deid_date.py file is that this file contains profiling code. 
Additionally, based on the results of the first profiling, the code has been modified: 
the two regular expressions within the deid_date function have been pre-compiled outside of the function.
"""

# Regex pattern to match dates in the following formats:
# MM/DD/YY, MM/DD/YYYY, MM/DD, M/D, M/DD, MM/D
# - MM can be 01-12, with or without a leading zero.
# - DD can be 01-31, with or without a leading zero.
# - YY and YYYY are 2 or 4 digit years respectively.
date_pattern = r'((0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[0-1])/\d{2,4}|(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[0-1]))'
# compiling the reg_ex would save sime time!
date_reg = re.compile(date_pattern)

# Precompiled regular expressions for efficiency
# start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
# where PATIENT is the patient number and NOTE is the note number.
start_of_record_reg = re.compile(r'^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$', re.IGNORECASE)
# end of each note has the patter: ||||END_OF_RECORD
end_of_record_reg = re.compile(r'\|\|\|\|END_OF_RECORD$')


def check_for_date(patient, note, chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for date occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find dates.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    
    
    offset = 27
    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient, note))
    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in date_reg.finditer(chunk):
        # debug print, 'end=" "' stops print() from adding a new line
        print(patient, note, end=' ')
        print((match.start()-offset), match.end()-offset, match.group())
        
        # The results of the search here are for each chunk in this record (that is, each patient record), not relative to the entire id.txt file.
        # In addition, what is recorded here is not the number of lines, but the number of characters, and an offset is also subtracted.   
        # create the string that we want to write to file ('start start end')        
        result = str(match.start()-offset) + ' ' + str(match.start()-offset) + ' ' + str(match.end()-offset)
        # write the result to one line of output
        output_handle.write(result+'\n')




def deid_date(text_path='id.text', output_path='date.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each date found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected date string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no date detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each date detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end date
        where `start` is the start position of the detected date string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # open the output file just once to save time on the time intensive IO
    with open(output_path, 'w+') as output_file:
        with open(text_path) as text:
             # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                # Using the precompiled regular expression for 'start_of_record' pattern matching.
                # This is an optimization over the original function where re.findall() was called with a string pattern,
                # causing the regular expression to be compiled on every iteration.
                record_start = start_of_record_reg.findall(line)
                if record_start:
                    patient, note = record_start[0]
                chunk += line
                record_end = end_of_record_reg.findall(line)
                if record_end:
                    check_for_date(patient, note, chunk.strip(), output_file)
                    # initialize the chunk for the next note to be read
                    chunk = ''


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    deid_date(sys.argv[1], sys.argv[2])
    profiler.disable()
    profiler.dump_stats("profile_results.prof")

    import pstats
    p = pstats.Stats("profile_results.prof")
    p.sort_stats("cumulative").print_stats(10)  # print top 10 time cost function
