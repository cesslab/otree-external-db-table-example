# oTree External Database Table Example
The purpose of this example program is to show how an external table can be used to share data between seperate otree sessions.

## The problem 
oTree does not, as of version 5.10, provide a method for sharing data across sessions (e.g. sharing advice between the first and eight session). 

## The Solution
A solution to this problem is to leverage the existing oTree database by adding a custom table to it which can be used to store and retrieve data across sessions.