# Movies-ETL

### Assumption Analysis

There were several columns in the wiki data that were consolidated and merged.  We merged several columns where the movie title was listed in order to reduce redundancy and increase readability of the data.  Further, we renamed the columns in the wiki data in order to further consolidate and create more consistancy in the headers of the data.  For example, 'Adaptation by', 'Screen story by', 'Screenplay by', 'Story by', and 'Written by' were all able to merge into one column titled "Writer(s)" to provide more concise, readable data on who wrote the movie. 

Another assumption applied to this data cleaning process was removing duplicate movie IDs.  In using regular expressions we were able to identify duplicate movie IDs and remove them from the data set. This allows our data to be more accurate and will not cause issue for future application of this data with the duplicates removed.

One can assume that columns with less than 90% null value provide no significant support to our data evaluation.  For example, 'Suggested by' column has 7032 null values in the column.  This is of no real use to our analysis purposes and is appropriate to parse away from our data.

When reviewing the box office data, the currency earned was reflected in a miriad of ways.  There were 3 main formats where box office earning is represented and we can use the data that fit into those 3 forms.  However, there are about 37 data points where the box office earnings were formatted inconsistently or in a different currency that we would have needed 37 different functions to make it usable for our purposes.  Instead we drop this data assuming 37 data points out of over 3,700 would not be statistically significant.  This assumption is applicable to the budget column as well.

After merging the data, we were able to compare data provided from both wiki and kaggle and drop data that was not as consistent, unifrom and more accurate.  For example, we dropped the wiki version of 'run time' and 'budget' because there were some outliers in the wiki data that were not present in the kaggle data.  This indicated possible damaged data and dropping that column allowed us to have the most accurate data. 
