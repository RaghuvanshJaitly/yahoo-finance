import numpy as np
class SimpleLinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0

#Finds the slope and y-intercept for our arrays
    def fit(self, X: np.ndarray, y: np.ndarray):
        n = len(X)
        sum_X = np.sum(X)
        sum_y = np.sum(y)
        xy = X * y
        sum_xy = np.sum(xy)
        x_square = np.square(X)
        sum_x_square = np.sum(x_square)
        sum_x_whole_sq = np.square(sum_X)
        self.slope = (n * sum_xy - (sum_X )* (sum_y))/(n * sum_x_square - (sum_x_whole_sq))
        self.intercept = (sum_y - (self.slope * sum_X))/ n
        return self.slope, self.intercept
    
# finds the best possible line using y = mx + b
    def predict(self, X: np.ndarray):
        y_fit = self.slope * X + self.intercept
        return y_fit
    
# Error from data points
    def residuals(self, X: np.ndarray, y: np.ndarray):
        y_fit = self.predict(X)
        res = y - y_fit
        return res
    
# squared residuals
    def squared_residuals(self, X: np.ndarray, y: np.ndarray):
        y_fit = self.predict(X)
        sq_res = np.square(y - y_fit)
        return sq_res

# linear regression chooses the slope and intercept that minimizes this value
    def SSE(self, X: np.ndarray, y: np.ndarray):
        y_fit = self.predict(X)
        sq_res = np.square(y - y_fit)
        sse = np.sum(sq_res)
        return sse

if __name__ == "__main__":
    X= np.array([1, 2, 3, 4, 5])
    y = np.array([3, 5, 7, 8, 11])
    model = SimpleLinearRegression()
    slope, intercept = model.fit(X, y)
    y_fit = model.predict(X)
    residual = model.residuals(X, y)
    squaered_residual = model.squared_residuals(X, y)
    sse = model.SSE(X, y)
    print(f"Slope: {slope}")
    print(f"y-Intercept: {intercept}")
    print(f"y-fit: {y_fit}")
    print(f"Residual: {residual}")
    print(f"Squared Residual: {squaered_residual}")
    print(f"Sum of Squared Errors: {sse}")
    