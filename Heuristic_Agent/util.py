
from math import fsum, log, exp

# -> from statistics import linear_regression
# Would love to use numpy.polyfit, but I can't get numpy installed correctly
# would love to use statistics.linear_regression, but can't get the required version for PyPy
# This is a copied and edited form of the linear_regression method from CPython Source
def linear_regression(x, y, proportional=False):
	n = len(x)
	if len(y) != n:
		raise ValueError('linear regression requires that both inputs have same number of data points')
	if n < 2:
		raise ValueError('linear regression requires at least two data points')
	if proportional:
		sxy = fsum(xi * yi for xi, yi in zip(x, y))
		sxx = fsum(xi * xi for xi in x)
	else:
		xbar = fsum(x) / n
		ybar = fsum(y) / n
		sxy = fsum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
		sxx = fsum((xi - xbar) ** 2 for xi in x)
	try:
		slope = sxy / sxx   # equivalent to:  covariance(x, y) / variance(x)
	except ZeroDivisionError:
		raise ValueError('x is constant')
	intercept = 0.0 if proportional else ybar - slope * xbar
	return (slope, intercept)


# calculates (a, b) such that y = b * exp(a * x) 
# returns y(xi)
def exponential_regression_eval(x, y, xi, proportional=False) :
	(a, b) = linear_regression(x, [log(yi) for yi in y], proportional=proportional)
	return exp(b) * exp(a * xi)


if __name__ == "__main__" :
	x = [1,2,3,4,5]
	y = [2,4,8,16,32]

	assert abs(exponential_regression_eval(x,y,10) - 1024) < 0.01
	print("Passed test (this test is very basic)")

