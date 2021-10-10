
"""
Linear
"""
func LinearInOut(t):
	return t

"""
Quadratic easing functions
"""


func QuadEaseInOut(t):
	if t < 0.5:
		return 2 * t * t
	return (-2 * t * t) + (4 * t) - 1


func QuadEaseIn(t):
	return t * t


func QuadEaseOut(t):
	return -(t * (t - 2))


"""
Cubic easing functions
"""


func CubicEaseIn(t):
	return t * t * t


func CubicEaseOut(t):
	return (t - 1) * (t - 1) * (t - 1) + 1


func CubicEaseInOut(t):
	if t < 0.5:
		return 4 * t * t * t
	var p:float = 2 * t - 2
	return 0.5 * p * p * p + 1


"""
Quartic easing functions
"""


func QuarticEaseIn(t):
	return t * t * t * t


func QuarticEaseOut(t):
	return (t - 1) * (t - 1) * (t - 1) * (1 - t) + 1


func QuarticEaseInOut(t):
	if t < 0.5:
		return 8 * t * t * t * t
	var p:float = t - 1
	return -8 * p * p * p * p + 1


"""
Quintic easing functions
"""


func QuinticEaseIn(t):
	return t * t * t * t * t


func QuinticEaseOut(t):
	return (t - 1) * (t - 1) * (t - 1) * (t - 1) * (t - 1) + 1


func QuinticEaseInOut(t):
	if t < 0.5:
		return 16 * t * t * t * t * t
	var p:float = (2 * t) - 2
	return 0.5 * p * p * p * p * p + 1


"""
Sine easing functions
"""


func SineEaseIn(t):
	return sin((t - 1) * PI / 2) + 1


func SineEaseOut(t):
	return sin(t * PI / 2)


func SineEaseInOut(t):
	return 0.5 * (1 - cos(t * PI))


"""
Circular easing functions
"""


func CircularEaseIn(t):
	return 1 - sqrt(1 - (t * t))


func CircularEaseOut(t):
	return sqrt((2 - t) * t)


func CircularEaseInOut(t):
	if t < 0.5:
		return 0.5 * (1 - sqrt(1 - 4 * (t * t)))
	return 0.5 * (sqrt(-((2 * t) - 3) * ((2 * t) - 1)) + 1)


"""
Exponential easing functions
"""


func ExponentialEaseIn(t):
	if t == 0:
		return 0
	return pow(2, 10 * (t - 1))


func ExponentialEaseOut(t):
	if t == 1:
		return 1
	return 1 - pow(2, -10 * t)


func ExponentialEaseInOut(t):
	if t == 0 or t == 1:
		return t

	if t < 0.5:
		return 0.5 * pow(2, (20 * t) - 10)
	return -0.5 * pow(2, (-20 * t) + 10) + 1


"""
Elastic Easing Functions
"""


func ElasticEaseIn(t):
	return sin(13 * PI / 2 * t) * pow(2, 10 * (t - 1))


func ElasticEaseOut(t):
	return sin(-13 * PI / 2 * (t + 1)) * pow(2, -10 * t) + 1


func ElasticEaseInOut(t):
	if t < 0.5:
		return (
			0.5
			* sin(13 * PI / 2 * (2 * t))
			* pow(2, 10 * ((2 * t) - 1))
		)
	return 0.5 * (
		sin(-13 * PI / 2 * ((2 * t - 1) + 1))
		* pow(2, -10 * (2 * t - 1))
		+ 2
	)


"""
Back Easing Functions
"""


func BackEaseIn(t):
	return t * t * t - t * sin(t * PI)


func BackEaseOut(t):
	var p:float = 1 - t
	return 1 - (p * p * p - p * sin(p * PI))


func BackEaseInOut(t):
	if t < 0.5:
		var p:float = 2 * t
		return 0.5 * (p * p * p - p * sin(p * PI))

	var p:float = 1 - (2 * t - 1)

	return 0.5 * (1 - (p * p * p - p * sin(p * PI))) + 0.5


"""
Bounce Easing Functions
"""


func BounceEaseIn(t):
	return 1 - BounceEaseOut(1 - t)


func BounceEaseOut(t):
	if t < 4 / 11:
		return 121 * t * t / 16
	elif t < 8 / 11:
		return (363 / 40.0 * t * t) - (99 / 10.0 * t) + 17 / 5.0
	elif t < 9 / 10:
		return (4356 / 361.0 * t * t) - (35442 / 1805.0 * t) + 16061 / 1805.0
	return (54 / 5.0 * t * t) - (513 / 25.0 * t) + 268 / 25.0


func BounceEaseInOut(t):
	if t < 0.5:
		return 0.5 * BounceEaseIn(t * 2)
	return 0.5 * BounceEaseOut(t * 2 - 1) + 0.5
