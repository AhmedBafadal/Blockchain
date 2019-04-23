# created a byte stream for proof of work
# need to order data upon loading as ordered dict and not a regular dict because upon hashing.. any slight variations in data structure renders the blockchain invalid. (e.g. dict is not indexed, if values appear in alternate order could impact hash)
# upon fixing loading files as ordered dict for correct hash reads, the problem remains unorderd dicts in open transactions. whereby if coins are not mined and multiple transactions take place, it will render the blockchain invalid.

# Issue arising using default argument in constructor of the Block class, time argument set to time() by default.
# This created the same time stamp because time() was only evaluated once. As such, the second block will recieve the same timestamp as the #first.
# Hashing a block as a class requires object to be converted to json. requires use of <class>.__dict__.copy(). (using copy to prevent #manipulating original blocks by hashing subsequent ones)