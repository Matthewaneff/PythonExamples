'''----------------------------------------------------------------------------
Name:              ConcatenaterowvalueArc.py
Purpose:           Concatenate row values for a specified field.
Author:            Esri
Created:           7/1/2012
Modified:          04/21/2013
ArcGIS Version:    10.1
Python Version:    2.6.1
-----------------------------------------------------------------------------'''

import collections
import arcpy
import locale
locale.setlocale(locale.LC_ALL, '')

def field_checker(from_field_type, to_field_type, delimiter):
    """A function to check for correct field types between the from and to fields."""

    if from_field_type == "String":
        if not to_field_type == "String":
            arcpy.AddError("Copy To Field must be of type text when Read From Field is of type text.")
    else:
        if not to_field_type == "String":
            if delimiter != "":
                arcpy.AddError("Copy To Field must be of type text when Read From Field is of type numeric or date and you are using a delimiter.")

            if delimiter == "":
                if from_field_type == "SmallInteger":
                    if not to_field_type in ["Integer",  "SmallInteger", "Float", "Double"]:
                        if to_field_type == "Date":
                            arcpy.AddError("Copy To Field must be of type text.")

                if from_field_type == "Integer":
                    if to_field_type in ["SmallInteger", "Integer", "Float", "Double", "Date"]:
                        arcpy.AddError("Copy To Field must be of type text.")

                else:
                    if from_field_type in ["Float", "Double" , "Date"]:
                        if to_field_type in ["Integer", "SmallInteger", "Float", "Double" , "Date"]:
                            arcpy.AddError("Copy To Field must be of type text.")

# End field_checker function

def concatenate(input_table, case_field, from_field, to_field, delimiter='', *args):
    """Function to concatenate row values."""

    # Get feild types for from and to fields.
    from_field_type = arcpy.ListFields(input_table, from_field)[0].type
    to_field_type = arcpy.ListFields(input_table, to_field)[0].type
    to_field_length = arcpy.ListFields(input_table, to_field)[0].length

    # Check that the from and to fields match correctly for concatenation.
    field_checker(from_field_type, to_field_type, delimiter)

    # Group a sequence of case field ID's and value pairs into a dictionary of lists.
    dictionary = collections.defaultdict(list)
    try:
        srows = None
        srows = arcpy.SearchCursor(input_table, '', '', '', '{0} A;{1} A'.format(case_field, from_field))
        for row in srows:
            case_id = row.getValue(case_field)
            value = row.getValue(from_field)
            if from_field in ['Double', 'Float']:
                value = locale.format('%s', (row.getValue(from_field)))
            if value <> None:
                dictionary[case_id].append(value)
    except RuntimeError as re:
        arcpy.AddError('Error in accessing {0}. {1}'.format(input_table, re.args[0]))
    finally:
        if srows:
            del srows
    try:
        urows = None
        urows = arcpy.UpdateCursor(input_table)
        for row in urows:
            case_id = row.getValue(case_field)
            values = dictionary[case_id]
            f = u''.join(unicode(val) for val in values)

            if not delimiter == '':
                if (len(f) + (len(values)-1)) > to_field_length:
                    arcpy.AddError('Length of the Copy to Field is less than the length of the content you are trying to copy.')
                else:
                    if from_field_type in ['String']:
                        if to_field_type in ['String']:
                            row.setValue(to_field, delimiter.join(sorted(set([val for val in values if not value is None]))))
                    else:
                        row.setValue(to_field, delimiter.join(sorted(set([str(val) for val in values if not value is None]))))
            else:
                if to_field_type in ['String']:
                    if len(f) > to_field_length:
                        arcpy.AddError('Length of the Copy to Field is less than the length of the content you are trying to copy.')
                else:
                    if from_field_type in ['String']:
                        if to_field_type in ['String']:
                            row.setValue(to_field, delimiter.join(sorted(set([val for val in values if not value is None]))))
                    else:
                        if to_field_type in ['String']:
                            row.setValue(to_field, delimiter.join(sorted(set([str(val) for val in values if not value is None]))))
                        elif to_field_type in ['Integer', 'SmallInteger'] :
                            row.setValue(to_field, int(delimiter.join(sorted(set([str(val) for val in values if not val is None])))))
                        elif to_field_type in ['Double', 'Float']:
                            row.setValue(to_field, float(delimiter.join(sorted(set([str(val) for val in values if not val is None])))))

            # Date formatting can be edited to match local.
            if from_field_type in ['Date']:
                row.setValue(sort(to_field, delimiter.join([val.strftime('%d%m%Y') for val in values if not val is None])))
            urows.updateRow(row)

    except RuntimeError as re:
        arcpy.AddError('Error updating {0}. {1}'.format(input_table, re.args[0]))
    finally:
        if urows:
            del urows

    # If you are using the tool in ModelBuilder, set the derived output parameter to the value
    # of input table so that it is not empty and can be used with other tools.
    arcpy.SetParameterAsText(5, str(input_table))

# End concatenate function

if __name__ == '__main__':
    argv = tuple(arcpy.GetParameterAsText(i)
             for i in range(arcpy.GetArgumentCount()))
    concatenate(*argv)
