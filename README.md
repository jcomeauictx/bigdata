I did this out of frustration with attempting to use Spark on Amazon EMR.

all the time I lost attempting to get the cluster to work with my Spark
scripts is apparently not going to be paid. so I hacked together something that
does the same thing as the Pandas scripts whose functionality I was attempting
to duplicate, on my own time, in about 48 hours. and it does it in a fraction
of the code, and it's better in that it weeds out duplicated data in the 
input files.

it's not fast enough yet, but as long as the tables to which you're joining
are small, it fits easily in RAM, and using `aws s3 cp`, you don't need to
store the output locally, you can stream it directly to an S3 bucket.
