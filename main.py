# // READ ME //
# the purpose of this code is to generate a list of students who will recieve an absence report
# 1000 students will recieve an absence report based on the following criteria:
# 1) students must have missed 5% >= and <= 50% of the total amount of days they were enrolled in school(s)
# 2) students must have missed more than 3 days of school for any reason
# 3) students must have an address to send the absence report
# 4) students must NOT be in the 11th grade and from the school where school_id = 1061
# priority will be given to students who have 1) >= 10% missed enrolled days and 2) students who are in elementary school (grades 1-5)

# thus, students with the following data will be NOT be eligible to recieve the absence report:
# 1) students without grades
# 2) students without addresses
# 3) students without schools
# 4) students who have been enrolled for more than 47 days
# 5) students who have been enrolled in school(s) for less than 20 days
# 6) students who have less than 3 absences
# 7) multiple students from the same household (only one student per household is eligible to recieve a report)

# import python libraries
import pandas as pd
import numpy as np

def import_absence_data():
    # this function imports the raw student absence data and creates a df for student absence data
    df_absences_raw = pd.read_csv("everydaylabs_studentabsences.csv")
    
    # return the df for future use
    return df_absences_raw

def import_address_data():
    # this function imports the raw student info/address data and creates a df for student address data
    df_address_raw = pd.read_csv("everydaylabs_studentinfo.csv")
    
    # return the df for future use
    return df_address_raw

def counting_abscence_days():
    # in order to determine which students are eligible to recieve a report, the total number absence days must be determined 
    # use the raw absence data
    df_absences_raw = import_absence_data()
    
    # there are multiple student_id entries in the raw absence data where each student entry = 1 absence day
    # count the number of times each student_id occurances to get the total number of absences per student
    absence_count = df_absences_raw["student_id"].value_counts()
    # transform the absence_count values into a df
    df_absence_count = pd.DataFrame(absence_count)
    # rename the second column as total_absences
    df_absence_count = df_absence_count.rename(columns={"student_id": "total_absences"})
    # rename the index column as student_id
    df_absence_count.index.name = "student_id"
    
    # return the df for future use
    return df_absence_count

def cleaning_raw_absence_data():
    # the raw absence data needs to be cleaned before it can be merged with the absence counts
    # use the raw absence data
    df_absence_raw = import_absence_data()
    
    # drop the following columns: absence_date, type, and export_date --> we will not need this data
    df_absence_clean = df_absence_raw.drop(columns=["absence_date", "type", "export_date"])
    # drop all records with duplicate student_id, enrolled_days, and grade values
    # don't drop any records where students went to multiple schools
    df_absence_clean = df_absence_clean.drop_duplicates(subset=["student_id", "enrolled_days", "grade"], keep="first")
    
    # return the df for future use
    return df_absence_clean # reminder: this df contains the values for students who went to more than one school

def finding_students_from_multiple_schools():
    # this purpose of this function is to find the students who went to multiple schools and sum their total enrollment dates
    # use the clean absence data 
    df_absence_clean = cleaning_raw_absence_data()
    
    # find the students who went to multiple schools and sort the records by by student_id
    df_keep_duplicates = pd.concat(g for _, g in df_absence_clean.groupby("student_id") if len(g) > 1)
    # sum the total enrolled days for students who went to multiple schools
    df_sum_enrolled_dates = df_keep_duplicates.groupby(["student_id", "grade"]).sum()
    # drop the school_id since we are retaining this information in the clean absence data
    df_sum_enrolled_days = df_sum_enrolled_dates.drop(columns=["school_id"])
    
    # return the df for future use
    return df_sum_enrolled_days # reminder: this df does not include the school_id

def retaining_all_school_ids():
    # this function will retain the current school_id for students who went to multiple schools
    # NOTE: it appears that the most recent record for each student is the current school that this student attends
    # use the clean absence data
    df_absence_clean = cleaning_raw_absence_data()
    
    # find the students who went to multiple schools and retain the most recent school (see note above)
    df_retain_school_ids = df_absence_clean.drop_duplicates(subset=["student_id"], keep="first")
    
    # return the df for future use
    return df_retain_school_ids # reminder: this df has all needed absence information and no duplicate records
    
def merge_absence_data():
    # this function will join all the absence data thus far into one df
    # use the absence count df to get total absence days for all students
    df_absence_count = counting_abscence_days() #note: student_id is already the index
    # use the df with all the retained school ids and no duplicate records
    df_retain_school_ids = retaining_all_school_ids()
    
    # to join, set the index as student_id
    df_retain_school_ids = df_retain_school_ids.set_index("student_id")
    # join the two dataframes together to get a final absence dataframe
    df_final_absence_data = df_absence_count.join(df_retain_school_ids, how="inner")
    
    # return the df for future use
    return df_final_absence_data # reminder: the total number of enrolled days here is WRONG for students who went to multiple schools
 
def get_all_enrollments():
    # the purpose of this function is to get the total enrollement days for students who went to multiple schools
    # use the df with all the merged absence values (and wrong number of enrolled days for students who went to multiple schools)
    df_final_absence_data = merge_absence_data()
    # use the df with all school_ids to make sure we can map the correct students to the value of enrolled_days
    df_retain_school_ids = retaining_all_school_ids()
    # use the df with the sum enrollement for students who went to multiple schools
    df_sum_enrolled_days = finding_students_from_multiple_schools()
   
    # this function will use dictionaries and mapping to get the correct number of enrolled_days to each student_id
    # reset this index so we can create a dictionary for this df
    df_sum_enrolled_days = df_sum_enrolled_days.reset_index()
    # reset this index so we can create a dictionary for this df
    df_final_absence_data = df_final_absence_data.reset_index()
    
    # create a dictionary from the student_ids and enrolled_days
    df_dict_1 = df_sum_enrolled_days.set_index("student_id").to_dict()["enrolled_days"]
    # map the dictionary to get the values stored in the dictionary
    df_final_absence_data["enrolled_days"] = df_final_absence_data.set_index(["student_id"]).index.map(df_dict_1.get)
    
    # create another dictionary from the student_ids and enrolled_days
    df_dict_2 = df_retain_school_ids.set_index("student_id").to_dict()["enrolled_days"]
    # map the dictionary to get the values stored in the dictionary
    df_final_absence_data["enrolled_days"].fillna(df_final_absence_data["student_id"].map(df_dict_2), inplace=True)
    
    # return the df for future use
    return df_final_absence_data # reminder: this is the absence data we want to use -- record integrity is good
    
def merge_all_data():
    # this function will merge all the absence data and student info (addresses) into one df so that it can be cleaned 
    # use the raw address data
    df_address_raw = import_address_data()
    # use the absence data with good record integrity 
    df_final_absence_data = get_all_enrollments()
    
    # set the index as student_id for the raw address data
    df_address_raw = df_address_raw.set_index("student_id")
    # set index as student_id for the absence data
    df_final_absence_data = df_final_absence_data.set_index("student_id")
    
    # join the absence and address data together into one df
    df_all_data = df_final_absence_data.join(df_address_raw, how="inner")
    
    # return the df for future use
    return df_all_data
    
def clean_all_data():
    # this function will clean the data for the absence report according to the requirements listed in the READ ME
    # use the df with all the absence and address data
    df_all_data = merge_all_data()
    
    # to recieve a report: students must have a mailing address
    # drop all records with empty address values (don't include postdirection, these can be null)
    df_all_nulls_omitted = df_all_data.dropna(subset=["school_id", "enrolled_days", "city", "street_number", "street_name", "street_type", "state"])   
    # students in 11th grade who go to school with a school_id = 1061 CANNOT recieve a report
    # drop all rows with school_id = 1061 and grade = 11
    df_drop_id1061 = df_all_nulls_omitted.drop(df_all_nulls_omitted[(df_all_nulls_omitted["school_id"] == 1061) & (df_all_nulls_omitted["grade"] == 11)].index)
    # to recieve a report: students must have more than 3 days of absences
    # drop all records with less than 3 days of absences
    df_drop_less_3 = df_drop_id1061.drop(df_drop_id1061[(df_drop_id1061["total_absences"] < 3)].index)
    # to recieve a report: students must be enrolled in school for more than 20 days
    # drop all records for students who have been enrolled for less than 20 days
    df_drop_less_20 = df_drop_less_3.drop(df_drop_less_3[(df_drop_less_3["enrolled_days"] < 20)].index)
    # the maximum number of days a student can be enrolled is 47 days
    # drop all records where the student is enrolled more than 47 days
    df_eligible_students = df_drop_less_20.drop(df_drop_less_20[(df_drop_less_20["enrolled_days"] > 47)].index)

    # return the df for future use
    return df_eligible_students

def ineligible_students():
    # this function will create a list of students ineligible to recieve an absence report according to the READ ME
    # use the df with all the absence and address data
    df_all_data = merge_all_data()
    df_all_data = df_all_data.reset_index()
    
    # dropping the postdirection column
    df_postdirection_dropped = df_all_data.drop(columns=["postdirection"])
    # keep all incomplete addresses and missing student_ids, school_ids, grades, enrolled_days, and attendance_days
    # everything that was complete, was dropped from the df
    df_ineligible_students = df_postdirection_dropped.loc[pd.isnull(df_postdirection_dropped).any(1), :]
    
    # return the df for future use
    return df_ineligible_students  

def calculate_percentage():
    # this function calculates the percentage of days that students were absent based on total_absences and total enrolled_days 
    # use the df with the data for all the eligible students
    df_eligible_students = clean_all_data()  
    # create new df to include the column for the percentage of days students were absent
    df_calculations = pd.DataFrame(df_eligible_students, columns=["total_absences", "enrolled_days", "school_id", "grade", "zip", "city", "street_number", "street_name", "street_type", "postdirection", "state", "percent_missed"])
    # reset the index for the df so calculations can be done
    df_calculations = df_calculations.reset_index()
    # calculate % of total enrolled days that each student missed
    df_calculations["percent_missed"] = (df_calculations["total_absences"]/df_calculations["enrolled_days"])*100
    
    # return the df for future use
    return df_calculations 

def determine_report_eligibility():
    # this function determines the eligibility of students to recieve a report based on the percentage of days missed (see READ ME)
    # use the df with the percentage calculations
    df_calculations = calculate_percentage()
    # evaluate students with missed absences 5% >= and <= 50% of total enrolled days
    df_evaluation = df_calculations.drop(df_calculations[(df_calculations["percent_missed"] < 5)].index)
    df_evaluation = df_evaluation.drop(df_evaluation[(df_evaluation["percent_missed"] > 50)].index)
    
    # return the df for future use
    return df_evaluation

def find_households():
    # this function finds the households with multiple students and picks only one student per household to be eligible for a report
    # use the evaluation df with all the data about students who are eligible for a report based on percent days missed
    df_evaluation = determine_report_eligibility()
    # find households with multiple students by locating duplicate addresses, sort by zip code
    df_households_sorted = df_evaluation[df_evaluation.duplicated(["zip", "city", "street_number", "street_name", "street_type", "postdirection", "state"], keep=False)].sort_values("zip")
    # drop all records where there are multiple students living at one address (only keep first student record at each address)
    df_all_records_ready = df_evaluation.drop_duplicates(subset=["zip", "city", "street_number", "street_name", "street_type", "postdirection", "state"], keep="first")  

    # return the df for future use
    return df_all_records_ready

def select_students():
    # this function selects 1000 students who will recieve an absence report
    # the criteria used in this function can be found in the READ ME
    # use the df with all records ready (only one student per household)
    df_all_records_ready = find_households()
    # use the ineligible student df so we can export the csv here
    df_ineligible_students = ineligible_students()
    
    # set a report_amt
    report_amt = 1000
    # drop all records where students missed less than 10% of total enrolled_days
    df_drop_attendance = df_all_records_ready.drop(df_all_records_ready[(df_all_records_ready["percent_missed"] < 10)].index)
    # drop all records for students not in grades 1-5 (elementary school)
    df_drop_grades = df_drop_attendance.drop(df_drop_attendance[(df_drop_attendance["grade"] > 5)].index)
    # retain these records so we can randomly pick from them later to reach the 1000 limit
    df_retain_grades = df_drop_attendance.drop(df_drop_attendance[(df_drop_attendance["grade"] < 6)].index)
    # reset the index for counting purposes
    df_absence_record = df_drop_grades.reset_index()
    # count the number of records to find how far off we are from 1000
    count = len(df_absence_record.index)
    # calculate the number of records we need to add
    add_n = report_amt - count
    # randomly pick add_n number of samples from the df with remaining eligible students (grades 6+)
    df_add_samples = df_retain_grades.sample(n=add_n)
    # append the record with grades 1-5 with random picks from grades 6+
    df_absence_record = df_absence_record.append(df_add_samples)
    # reset the index so we can assign a unique_id to each student who is recieving a report
    df_absence_record = df_absence_record.reset_index()
    # assign a random unique id to each student who will recieve an absence report
    df_absence_record["unique_id"] = np.sort(np.random.randint(1000, 5000, len(df_absence_record)))
    df_absence_record = df_absence_record.drop(columns=["level_0", "index"])
    
    # export this df as csv for the deliverable: the 1000 students who will be recieving an absence report
    df_absence_record.to_csv("final_1000_student_absence_report.csv")
    # export the ineligible student df as a csv for the deliverable: students ineligible to recieve a report
    df_ineligible_students.to_csv("final_ineligible_students.csv")
    
    # finally, return the df with our final 1000 students
    return df_absence_record
    
select_students()
    