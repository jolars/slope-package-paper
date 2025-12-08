#include <Eigen/Dense>
#include <iostream>
#include <slope.h>

int main() {
  Eigen::MatrixXd x(10, 3);
  Eigen::VectorXd y(10);

  // clang-format off
  x << 1, 2, 3,
       4, 5, 6,
       7, 8, 9,
       1, 0, 1,
       0, 1, 0,
       2, 1, 3,
       3, 2, 1,
       4, 0, 2,
       0, 3, 1,
       1, 1, 1;
  // clang-format on

  y << 1, 2, 3, 1, 0, 2, 1, 3, 0, 1;

  slope::Slope model;

  // Lasso
  model.setLambdaType("lasso");
  auto fit_lasso = model.path(x, y);

  // SLOPE
  model.setLambdaType("bh");
  model.setQ(0.2);
  auto fit_slope = model.path(x, y);

  Eigen::VectorXd coef_lasso = fit_lasso.getCoefs().back();
  Eigen::VectorXd coef_slope = fit_slope.getCoefs().back();

  std::cout << "Lasso Coefficients:" << std::endl << coef_lasso << std::endl;
  std::cout << "SLOPE Coefficients:" << std::endl << coef_slope << std::endl;

  // Cross-Validation
  auto cv_res = slope::crossValidate(model, x, y);
  auto best_params = cv_res.best_params;

  std::cout << "\nBest parameters from Cross-validation:" << std::endl;
  for (const auto &param : best_params) {
    printf("%-6s: %g\n", param.first.c_str(), param.second);
  }

  return 0;
}
